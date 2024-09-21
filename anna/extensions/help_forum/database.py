import motor.motor_asyncio
from typing import List, Optional
from pymongo import ReturnDocument


class HelpDatabase:
    def __init__(self, db_url: str, db_name: str):
        self.db_url = db_url
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self) -> None:
        if not self.client:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_url)
            self.db = self.client[self.db_name]

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    async def create_tables(self) -> None:
        await self.connect()
        # MongoDB collections are created automatically when we first insert documents
        pass

    async def get_config(self, guild_id: int) -> Optional[dict]:
        await self.connect()
        config = await self.db.config.find_one({"guild_id": guild_id})
        return config

    async def set_config(
        self, guild_id: int, help_forum_id: int, ping_role_id: int
    ) -> None:
        await self.connect()
        await self.db.config.insert_one(
            {
                "guild_id": guild_id,
                "help_forum_id": help_forum_id,
                "ping_role_id": ping_role_id,
            }
        )

    async def update_config(
        self, guild_id: int, help_forum_id: int, ping_role_id: int
    ) -> None:
        await self.connect()
        await self.db.config.find_one_and_update(
            {"guild_id": guild_id},
            {"$set": {"help_forum_id": help_forum_id, "ping_role_id": ping_role_id}},
            return_document=ReturnDocument.AFTER,
        )

    async def create_thread(
        self, thread_id: int, guild_id: int, help_forum_id: int, author_id: int
    ) -> None:
        await self.connect()
        await self.db.threads.insert_one(
            {
                "thread_id": thread_id,
                "guild_id": guild_id,
                "help_forum_id": help_forum_id,
                "author_id": author_id,
                "has_first_message": False,
                "closed": False,
            }
        )

    async def set_has_first_message(self, thread_id: int) -> None:
        await self.connect()
        await self.db.threads.update_one(
            {"thread_id": thread_id}, {"$set": {"has_first_message": True}}
        )

    async def is_thread_closed(self, thread_id: int) -> bool:
        await self.connect()
        thread = await self.db.threads.find_one({"thread_id": thread_id})
        return thread["closed"] if thread else False

    async def close_thread(self, thread_id: int) -> None:
        await self.connect()
        await self.db.threads.update_one(
            {"thread_id": thread_id}, {"$set": {"closed": True}}
        )

    async def open_thread(self, thread_id: int) -> None:
        await self.connect()
        await self.db.threads.update_one(
            {"thread_id": thread_id}, {"$set": {"closed": False}}
        )

    async def get_thread(self, thread_id: int) -> Optional[dict]:
        await self.connect()
        thread = await self.db.threads.find_one({"thread_id": thread_id})
        return thread

    async def get_forum_threads(self, help_forum_id: int) -> List[dict]:
        await self.connect()
        threads = self.db.threads.find({"help_forum_id": help_forum_id})
        return await threads.to_list(length=100)

    async def get_guild_threads(self, guild_id: int) -> List[dict]:
        await self.connect()
        threads = self.db.threads.find({"guild_id": guild_id})
        return await threads.to_list(length=100)

    async def get_user_threads(self, author_id: int) -> List[dict]:
        await self.connect()
        threads = self.db.threads.find({"author_id": author_id})
        return await threads.to_list(length=100)

    async def get_all_threads(self) -> List[dict]:
        await self.connect()
        threads = self.db.threads.find()
        return await threads.to_list(length=100)

    async def get_helpban_guild(self, guild_id: int) -> List[dict]:
        await self.connect()
        helpbans = self.db.helpban.find({"guild_id": guild_id})
        return await helpbans.to_list(length=100)

    async def get_helpban_user(self, user_id: int, guild_id: int) -> Optional[dict]:
        await self.connect()
        helpban = await self.db.helpban.find_one(
            {"user_id": user_id, "guild_id": guild_id}
        )
        return helpban

    async def set_helpban(
        self, user_id: int, banner_id: int, guild_id: int, reason: str
    ) -> None:
        await self.connect()
        await self.db.helpban.insert_one(
            {
                "user_id": user_id,
                "banner_id": banner_id,
                "guild_id": guild_id,
                "reason": reason,
            }
        )

    async def remove_helpban(self, user_id: int, guild_id: int) -> None:
        await self.connect()
        await self.db.helpban.delete_one({"user_id": user_id, "guild_id": guild_id})

    async def clear_helpban(self, guild_id: int) -> None:
        await self.connect()
        await self.db.helpban.delete_many({"guild_id": guild_id})
