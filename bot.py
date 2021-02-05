import asyncio
import os
import sys

from typing import Optional

import aiohttp
import discord

from discord.ext import commands
from pymongo.errors import ServerSelectionTimeoutError

from core.database import DatabaseManager
from core.logging import log_message

initial_cogs = [
    "cogs.audit",
    "cogs.admin",
    "cogs.general",
    "cogs.roles",
    "cogs.owner"
]


async def _get_prefix(self, ctx):
    guild_conf = await self.db.get_guild_config(ctx.guild.id)



class TownBoat(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(command_prefix="=", intents=intents, owner_id=os.environ["TOWNBOAT_OWNER"],
                         chunk_guilds_at_startup=False, heartbeat_timeout=150.0,
                         allowed_mentions=discord.AllowedMentions.none())
        self.session = Optional[aiohttp.ClientSession]
        self.remove_command("help")

        try:
            self.db = DatabaseManager(mongo_uri=os.environ["TOWNBOAT_MONGO"], loop=self.loop)
        except KeyError:
            log_message('err', 0, 'database', 'database', "mongo uri is missing from your env")
            sys.exit(0)
        except ServerSelectionTimeoutError:
            log_message('err', 0, 'database', 'database', 'connection timed out, make sure your IP is whitelisted.')
            sys.exit(0)
        except Exception as e:
            log_message('err', 0, 'database', 'database', e)
            sys.exit(0)

    async def on_connect(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)
        log_message("info", 0, "central", "central", "connected")

    async def on_ready(self) -> None:
        log_message('info', 0, 'central', 'central', 'ready')

        for extension in initial_cogs:
            try:
                self.load_extension(extension)
                log_message("info", "0", "central", "cog_loader", f"successfully loaded {extension}")
            except Exception as e:
                log_message("err", 0, "central", "cog_loader", f"failed to load {extension}\n{e}")

    def run(self):
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
                log_message('err', 0, "central", "central", "all pending tasks have been stopped")
            finally:
                log_message('err', 0, 'central', 'central', "shutting down bot")


bot = TownBoat()
bot.run()
