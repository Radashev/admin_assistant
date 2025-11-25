from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global mongo_client

    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.mongo_url)

    return mongo_client


def get_mongo_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB]
