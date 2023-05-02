import os

import dotenv
from httpx import AsyncClient, HTTPError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError

dotenv.load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]

class Vinomofo:

    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client
        self.items_collection: AsyncIOMotorCollection = client.vm_uncovered.items

    async def _vm_lookup(self, search_text: str|int, results_per_page: int = 18) -> list[dict]:
        url = "https://www.vinomofo.com/offer_searches.json"

        params = {"per_page": results_per_page, "q": search_text, "page": 1}

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        async with AsyncClient(timeout=6.0) as session:
            response = await session.get(url, headers=headers, params=params)
            response.raise_for_status()
            rj = response.json()

        items = rj.get("items", [])

        return items


    async def get_wine_by_url(self, slug: str) -> dict:
        items = await self._vm_lookup(slug)
        for item in items:
            if item['slug'] == slug:
                return item
        else:
            return {}

    async def bulk_update(self) -> None:
        items = await self._vm_lookup(search_text="", results_per_page=300)
        for item in items:
            await self.items_collection.replace_one(
                {"offer_id": item["offer_id"]},
                item,
                upsert=True
            )
        print(f"Upserted {len(items)} to DB")

    async def get_wine_from_vm(self, offer_id: int|str) -> dict:
        items = await self._vm_lookup(offer_id)

        if not items:
            return {}

        for item in items:
            if item["offer_id"] == int(offer_id):
                return item
        else:
            return {}

    async def get_wine_from_db(self, by: str, search_query: str|int) -> dict:
        try:
            result = await self.client.vm_uncovered.items.find_one(
                {by: search_query},
                {"_id": False},
                max_time_ms=1000
                )

            if not result and by == "offer_id":
                query = {
                    "slug": {
                        "$regex": f'{search_query}$',
                        "$options" :'i' # case-insensitive
                        }
                    }
                result = await self.client.vm_uncovered.items.find_one(
                    query,
                    {"_id": False},
                    max_time_ms=1000
                    )
            return result or {}
        except ServerSelectionTimeoutError:
            print("Unable to connect to DB")
            return {}

    async def get_random_wine_from_db(self) -> dict: # type: ignore
        sample = [{'$sample': {'size': 1 }}]
        async for rec in self.items_collection.aggregate(sample):
            return rec

    async def get_wine(self, search_query: str) -> dict:
        if is_url(search_query):
            slug = get_slug(search_query)
            print(slug)
            db_result = await self.get_wine_from_db("slug", slug)
            if db_result:
                return db_result
            else:
                web_result = await self.get_wine_by_url(slug)

        else:
            # Offer ID passed by user 
            db_result = await self.get_wine_from_db("offer_id", int(search_query))
            if db_result:
                print(f'db result for {search_query=}')
                return db_result
            else:
                # Offer ID has not been cached yet
                print(f'no db result for {search_query=}')
                try:
                    web_result = await self.get_wine_from_vm(search_query)
                except HTTPError as err:
                    print(f"Timeout: {err}")
                    return {}

        if web_result:
            print(f'web result for {search_query=}')
            try:
                _ = await self.client.vm_uncovered.items.insert_one(web_result)
                print('db updated')
            except ServerSelectionTimeoutError:
                print("Unable to update DB. No connection available")
            return web_result
        else:
            print(f'no web result for {search_query=}')
            return {}

async def validate_offer_id(offer_id: str|int) -> int:
    if isinstance(offer_id, int) and offer_id < 9999999:
        return offer_id

    if isinstance(offer_id, str):
        if offer_id.isdigit():
            return int(offer_id)

    raise ValueError(f"Offer ID {offer_id} is not numeric")

def is_url(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_slug(url: str) -> str:
    urlonly = url.split("?")[0]
    slug = urlonly.split("/")[-1]
    return slug
