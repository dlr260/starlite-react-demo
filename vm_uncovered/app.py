import os
from typing import cast

import dotenv
from controller import IndexController
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings
from starlite import CORSConfig, Starlite, State, TemplateConfig
from starlite.middleware import LoggingMiddlewareConfig
from starlite.template.jinja import JinjaTemplateEngine

dotenv.load_dotenv()

logging_middleware_config = LoggingMiddlewareConfig()

class AppSettings(BaseSettings):
    DATABASE_URL: str = os.environ["MONGO_URL"]
    SERVER_SELECT_TIMEOUT: int = int(os.getenv("SERVER_SELECT_TIMEOUT", 1000))

settings = AppSettings()

CORS_ALLOW = os.getenv("CORS_HOSTS", "*")
cors_config = CORSConfig(allow_origins=[CORS_ALLOW])

async def get_db_client(state: State) -> AsyncIOMotorClient:
    if not getattr(state, "client", None):
        state.client = AsyncIOMotorClient(
            settings.DATABASE_URL, 
            serverSelectionTimeoutMS=settings.SERVER_SELECT_TIMEOUT,
            tz_aware=True
        )
    return cast("AsyncIOMotorClient", state.client)

app = Starlite(
    route_handlers=[IndexController], 
    #template_config=TemplateConfig(directory="templates", engine=JinjaTemplateEngine, engine_callback=engine_callback), # type:ignore
    on_startup=[get_db_client],
    cors_config=cors_config,
    debug=True
)
