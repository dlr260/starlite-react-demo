from datetime import datetime
from typing import Dict, List, Optional

from models import Vinomofo, validate_offer_id
from starlite import Controller, Parameter, Redirect, Request, Response, State, Template, get
from starlite.status_codes import HTTP_302_FOUND


class IndexController(Controller):

    @get("/api")
    async def api_get_offer(self, state: State, offer_id: str = Parameter(query="offer_id")) -> dict:
        print(f"{datetime.now()}: api called")
        if not offer_id:
            return {}

        vm = Vinomofo(state.client)
        # try:
        response = await vm.get_wine(offer_id)
        # print(f"got response for {offer_id}")
        # print(response)
        # except:
        #     return {"errors": {"offerId": offer_id}}

        if not response.get("offer_id"):
            return {"errors": {"offerId": offer_id}}
        else:
            return response


    @get("/api/vm", name="vm")
    async def wine_lookup(self, state: State, offer_id: Optional[str] = Parameter(query="offer_id")) -> Template:
        LANDING_PAGE = Template(name="daisy.html", context={"result": None})
        vm = Vinomofo(state.client)

        if not offer_id:
            print("No offer id")
            # return default landing page
            return LANDING_PAGE

        try:
            print(f"offer id {offer_id}")
            # offer_id_int = await validate_offer_id(offer_id)
            response = await vm.get_wine(offer_id)
            if response:
                template = Template(name="daisy.html", context={"result": response})
            else:
                raise ValueError(f"Could not find match for Offer ID {offer_id}")
        except ValueError as err:
            # Display some error message
            print(f"value error was caught - {err}")
            ctx = {
                "error": {"message":err},
                "result": ""
                }
            template = Template(name="daisy.html", context=ctx)

        return template

