from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Create database connection."""
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        cls.db = cls.client.moodify  # database name
        
    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            
    @classmethod
    async def get_db(cls):
        """Get database instance."""
        return cls.db

# Database collections
class Collections:
    MOODS = "moods"
    JOURNALS = "journals"
    PLAYLISTS = "playlists" 