import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConfigurationError

from core.logging import log_message


class DatabaseManager:
    def __init__(self, mongo_uri: str, *, loop: asyncio.AbstractEventLoop=None) -> None:

        try:
            self.mongo = AsyncIOMotorClient(mongo_uri).townboat
        except ConfigurationError as e:
            log_message('err', 0, 'database', 'database', e)
