import asyncio
import os
from typing import Any, Dict, List, Optional, Union

import aiohttp
import discord

from discord.ext import commands

from core.database import DatabaseManager
from core.logging import log_message


class TownBoat(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(command_prefix="!", intents=intents, owner_id=os.environ["TOWNBOAT_OWNER"],
                         chunk_guilds_at_startup=False, heartbeat_timeout=150.0,
                         allowed_mentions=discord.AllowedMentions.none())
        self.session = Optional[aiohttp.ClientSession] = None
        # self.db = DatabaseManager(os.environ["TOWNBOAT_MONGO"], self.loop)

    async def on_connect(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)
        log_message("info", 0, "central", "central", "connected")

    async def on_ready(self) -> None:
        log_message('info', 0, 'central', 'central', 'ready')

    def run(self, *args, **kwargs):
        try:
            self.loop.run_until_complete(self.start(os.environ["TOWNBOAT_TOKEN"]))
        except KeyboardInterrupt:
            log_message("err", 0, "central", "central", "keyboard interrupted loop, exiting")
        except discord.LoginFailure:
            log_message('err', 0, "central", "central", "invalid token")
        except discord.PrivilegedIntentsRequired:
            log_message("err", 0, 'central', 'central', "intents are not enabled on the dashboard")
        except Exception as e:
            log_message("err", 0, "central", "central", f"{e}")
        finally:
            self.loop.run_until_complete(self.logout())
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            try:
                self.loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(self.loop)))
            except asyncio.CancelledError:
                log_message('err', 0, "central", "central", f"all pending tasks have been stopped")
            finally:
                log_message('err', 0, 'central', 'central', f"shutting down bot")


bot = TownBoat()
bot.run()
