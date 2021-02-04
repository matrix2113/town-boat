import discord

from discord.ext import commands

from core.utility import lower
from core.database import DEFAULT
from core.errors import BotMissingPermissionsInChannel


class AdminConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(manage_server=True)
    async def setlog(self, ctx, log: lower, channel: discord.TextChannel = None):
        chn_id = None
        if channel:
            try:
                await channel.send("Logs will be sent here")
            except discord.Forbidden:
                raise BotMissingPermissionsInChannel(["send_messages"], channel)
            chn_id = str(channel.id)

        keys = DEFAULT['logs'].keys()

        if log == 'all':
            for i in keys:
                await self.bot.db.update_guild_config(ctx.guild.id, {"$set": {f"logs.{i}": chn_id}})
        else:
            if log not in keys:
                raise commands.BadArgument("Invalid key. Valid keys are shown here\n" + ', '.join(keys))

            await self.bot.db.update_guild_config(ctx.guild.id, {'$set': {f'logs.{log}': chn_id}})
            await ctx.send("Completed!")



def setup(bot):
    bot.add_cog(AdminConfig(bot))