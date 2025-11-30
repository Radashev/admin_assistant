from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.db.mongo import get_mongo_client


async def add_task_to_db(telegram_id: int, text: str):
    client: AsyncIOMotorClient = get_mongo_client()
    db = client[settings.MONGO_DB]

    task = {"telegram_id": telegram_id, "text": text, "timestamp": datetime.utcnow()}

    result = await db.tasks.insert_one(task)
    return str(result.inserted_id)


async def get_tasks_from_db(telegram_id: int, limit: int = 20):
    client: AsyncIOMotorClient = get_mongo_client()
    db = client[settings.MONGO_DB]

    cursor = db.tasks.find({"telegram_id": telegram_id}).sort("timestamp", -1).limit(limit)
    tasks = await cursor.to_list(length=limit)
    return tasks
