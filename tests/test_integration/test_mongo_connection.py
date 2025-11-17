import pytest

from app.db.mongo import get_mongo_db


@pytest.mark.asyncio
async def test_mongo_connection():
    db = get_mongo_db()

    collections = await db.list_collection_names()

    assert isinstance(collections, list)
