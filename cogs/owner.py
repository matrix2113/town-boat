import discord
from datetime import datetime
from discord.ext import commands
import inspect
import io
import textwrap
import traceback
import os

from core import logging
from contextlib import redirect_stdout
from core.paginator import Pages


owners = [332196248993923073]


def is_owner():
    def predicate(ctx):
        return ctx.message.author.id in owners

    return commands.check(predicate)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    async def load(self, ctx, extension_name: str):
        """Loads an extension."""
        extension_name = f"cogs.{extension_name}"
        if not ctx.author.id in owners: return  # not an owner
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send("{} loaded.".format(extension_name))
        logging.log_message("debug", "0", f"{ctx.author}", f"{ctx.guild.name}", msg=f"loaded {extension_name}")

    @commands.command(hidden=True)
    @is_owner()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""
        extension_name = f"cogs.{extension_name}"
        if not ctx.author.id in owners: return
        self.bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))
        logging.log_message("debug", "0", f"{ctx.author}", f"{ctx.guild.name}", msg=f"unloaded {extension_name}")

    @commands.command(hidden=True)
    @is_owner()
    async def reload(self, ctx, extension_name: str):
        """Reload an extension."""
        extension_name = f"cogs.{extension_name}"
        if not ctx.author.id in owners: return
        self.bot.unload_extension(extension_name)
        self.bot.load_extension(extension_name)
        await ctx.send("`{}` reloaded.".format(extension_name))
        logging.log_message("debug", "0", f"{ctx.author}", f"{ctx.guild.name}", msg=f"reloaded {extension_name}")

    @commands.command(hidden=True, aliases=["e"])
    @is_owner()
    async def eval(self, ctx, *, body):
        """Evaluates python code"""

        # if ctx.author.id not in config["owners"]:
        #    return await ctx.send("That's not gonna happen lmao")

        env = {
            "ctx": ctx,
            "bot": self.bot,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "source": inspect.getsource,
            "os": os,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            """Simple generator that paginates text."""
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text) - 1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != "", pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")
            return await ctx.message.add_reaction("\u2049")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            err = await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:
                        out = await ctx.send(f"```py\n{value}\n```")
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f"```py\n{page}\n```")
                                break
                            await ctx.send(f"```py\n{page}\n```")
            else:
                self.bot._last_result = ret
                try:
                    out = await ctx.send(f"```py\n{value}{ret}\n```")
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f"```py\n{page}\n```")
                            break
                        await ctx.send(f"```py\n{page}\n```")

        if out:
            await ctx.message.add_reaction("\u2705")  # tick
        elif err:
            await ctx.message.add_reaction("\u2049")  # x
        else:
            await ctx.message.add_reaction("\u2705")

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")


def setup(bot):
    bot.add_cog(Owner(bot))