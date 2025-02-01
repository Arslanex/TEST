from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os
from dotenv import load_dotenv

class DatabaseConfig:
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    def initialize(cls, mongodb_url: Optional[str] = None, db_name: Optional[str] = None) -> None:
        load_dotenv()
        mongodb_url = mongodb_url or os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        db_name = db_name or os.getenv('MONGODB_DB', 'article_scraper')

        if cls._client is None:
            try:
                cls._client = AsyncIOMotorClient(mongodb_url)
                cls._database = cls._client[db_name]
                print(f"✅ Connected to MongoDB: {db_name}")
            except Exception as e:
                print(f"❌ Error connecting to MongoDB: {e}")
                raise

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        if cls._database is None:
            cls.initialize()
        return cls._database

    @classmethod
    def close(cls) -> None:
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._database = None
            print("🔌 MongoDB connection closed")
