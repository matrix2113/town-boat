import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


class DatabaseManager:
    def __init__(self, mongo_uri: str, *, loop: asyncio.AbstractEventLoop=None) -> None:
        self.mongo = AsyncIOMotorClient(mongo_uri)
        self.coll = self.mongo.townboat.guilds
