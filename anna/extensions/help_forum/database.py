import aiosqlite
from typing import List, Optional


class Database:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    async def connect(self) -> None:
        if not self.connection:
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            await self.connection.execute("PRAGMA foreign_keys = ON")

    async def disconnect(self) -> None:
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def create_tables(self) -> None:
        try:
            await self.connect()
            await self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    guild_id BIGINT PRIMARY KEY UNIQUE,
                    help_forum_id BIGINT NOT NULL,
                    ping_role_id BIGINT NOT NULL
                )
            """
            )
            await self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS threads (
                    thread_id BIGINT PRIMARY KEY,
                    help_forum_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    author_id BIGINT NOT NULL,
                    has_first_message BOOLEAN NOT NULL DEFAULT FALSE,
                    closed BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (guild_id) REFERENCES config(guild_id)
                )
            """
            )
            await self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS helpban (
                    user_id BIGINT PRIMARY KEY,
                    banner_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY (guild_id) REFERENCES config(guild_id)
                );
            """
            )
            await self.connection.commit()

        finally:
            await self.disconnect()

    async def get_config(self, guild_id: int) -> Optional[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM config WHERE guild_id = ?", (guild_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None

        finally:
            await self.disconnect()

    async def set_config(
        self, guild_id: int, help_forum_id: int, ping_role_id: int
    ) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO config (guild_id, help_forum_id, ping_role_id)
                    VALUES (?, ?, ?)""",
                    (guild_id, help_forum_id, ping_role_id),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def update_config(
        self, guild_id: int, help_forum_id: int, ping_role_id: int
    ) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE config SET help_forum_id = ?, ping_role_id = ? WHERE guild_id = ?""",
                    (help_forum_id, ping_role_id, guild_id),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def create_thread(
        self, thread_id: int, guild_id: int, help_forum_id: int, author_id: int
    ) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO threads (thread_id, guild_id, help_forum_id, author_id)
                    VALUES (?, ?, ?, ?)""",
                    (thread_id, guild_id, help_forum_id, author_id),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def set_has_first_message(self, thread_id: int) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE threads SET has_first_message = TRUE WHERE thread_id = ?""",
                    (thread_id,),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def is_thread_closed(self, thread_id: int) -> bool:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT closed FROM threads WHERE thread_id = ?", (thread_id,)
                )
                row = await cursor.fetchone()[0]
                return dict(row) if row else None

        finally:
            await self.disconnect()

    async def close_thread(self, thread_id: int) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE threads SET closed = TRUE WHERE thread_id = ?""",
                    (thread_id,),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def open_thread(self, thread_id: int) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE threads SET closed = FALSE WHERE thread_id = ?""",
                    (thread_id,),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def get_thread(self, thread_id: int) -> Optional[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM threads WHERE thread_id = ?", (thread_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None

        finally:
            await self.disconnect()

    async def get_forum_threads(self, help_forum_id: int) -> List[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM threads WHERE help_forum_id = ?", (help_forum_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        finally:
            await self.disconnect()

    async def get_guild_threads(self, guild_id: int) -> List[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM threads WHERE guild_id = ?", (guild_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        finally:
            await self.disconnect()

    async def get_user_threads(self, author_id: int) -> List[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM threads WHERE author_id = ?", (author_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        finally:
            await self.disconnect()

    async def get_all_threads(self) -> List[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM threads")
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        finally:
            await self.disconnect()

    async def get_helpban_guild(self, guild_id: int) -> List[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM helpban WHERE guild_id = ?", (guild_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        finally:
            await self.disconnect()

    async def get_helpban_user(self, user_id: int, guild_id: int) -> Optional[dict]:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM helpban WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild_id),
                )
                row = await cursor.fetchone()
                return dict(row) if row else None

        finally:
            await self.disconnect()

    async def set_helpban(
        self, user_id: int, banner_id: int, guild_id: int, reason: str
    ) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO helpban (user_id, banner_id, guild_id, reason)
                    VALUES (?, ?, ?, ?)""",
                    (user_id, banner_id, guild_id, reason),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def remove_helpban(self, user_id: int, guild_id: int) -> None:
        try:
            await self.connect()
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    DELETE FROM helpban WHERE user_id = ? AND guild_id = ?""",
                    (user_id, guild_id),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()

    async def clear_helpban(self, guild_id: int) -> None:
        try:
            await self.connect()
            print(guild_id)
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    """
                    DELETE FROM helpban WHERE guild_id = ?""",
                    (guild_id,),
                )
                await self.connection.commit()

        finally:
            await self.disconnect()


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    exit(1)