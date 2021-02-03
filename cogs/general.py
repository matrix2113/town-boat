import discord
import humanize
import os

from datetime import datetime
from discord.ext import commands

from core.paginator import HelpPaginator, CannotPaginate
from core import logging


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        latency = self.bot.latency
        embed = discord.Embed(title=f"Town Boat Latency", description=f"**{int(latency * 1000)}** ms",
                              timestamp=datetime.utcnow(), color=discord.Color.purple())
        embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
            logging.log_message("info", ctx.guild.shard_id, ctx.author, ctx.guild, f"successfully deleted {ctx.command} msg")
        except discord.Forbidden as e:
            logging.log_message("err", ctx.guild.shard_id, ctx.author, ctx.guild, f"could not delete ping msg\n{e}")

    @commands.command()
    async def botinfo(self, ctx):
        embed = discord.Embed(title="Town Boat Information", color=discord.Color.blue())
        embed.add_field(name="Latency", value=f"{int(self.bot.latency * 1000)} ms")
        embed.add_field(name="Shards", value=self.bot.shard_count)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""
        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            logging.log_message("err", ctx.guild.shard_id, ctx.author, ctx.guild, e)

        try:
            await ctx.message.delete()
        except discord.Forbidden as e:
            logging.log_message("err", ctx.guild.shard_id, ctx.author, ctx.guild, e)

    @commands.command(aliases=["whois", "userinfo", "ui"])
    async def profile(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        badges = ""

        if user.bot:
            badges += "🤖 "
        if user == ctx.guild.owner:
            badges += "👑 "

        embed = discord.Embed(colour=discord.Colour.purple(), timestamp=ctx.message.created_at,
                              title=f"User Info - {user}", description=badges)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name="ID:", value=user.id, inline=True)
        embed.add_field(name="Highest Role:", value=user.top_role.mention, inline=True)

        acc_creation = datetime.utcnow() - user.created_at
        acc_join = datetime.utcnow() - user.joined_at
        created_acc = humanize.precisedelta(acc_creation, suppress=["days", "hours", "minutes", "seconds"], format="%0.f")
        joined_acc = humanize.precisedelta(acc_join, suppress=["days", "hours", "minutes", "seconds"], format="%0.f")
        embed.add_field(name="Created Account On:",
                        value=user.created_at.strftime("%d %B %Y") + " (" + created_acc + " ago)", inline=False)
        embed.add_field(name="Joined Guild On:",
                        value=user.joined_at.strftime("%d %B %Y") + " (" + joined_acc + " ago)", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))