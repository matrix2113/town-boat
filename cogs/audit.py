from datetime import datetime, timedelta
from typing import Any, List, Union

import discord

from discord.ext import commands
from core.utility import QuickId, format_delta


class Audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def msg_cache(self):
        await self.bot.wait_until_ready()

        after = datetime.utcnow()
        after -= timedelta(minutes=30)

        for i in self.bot.get_all_channels:
            if isinstance(i, discord.TextChannel):
                try:
                    msgs = await i.history(limit=30, after=after).flatten()
                except discord.Forbidden:
                    pass
                else:
                    if not msgs:
                        msgs = await i.history(limit=5).flatten()
                    self.bot._connection._messages += msgs

    async def check_enabled(self, guild_id: int, item: Any):
        data = await self.bot.db.get_guild_config(guild_id)
        try:
            return self.bot.get_channel(int(data.logs.get(item, 0)))
        except (ValueError, TypeError):
            return data.get(item, False)

    async def push_audit(self, log: discord.TextChannel, payload: Union[
        discord.Message, discord.TextChannel, discord.VoiceChannel, discord.Role, int, discord.RawMessageDeleteEvent],
                         raw: bool, end: str = None, *, mode: str = None,
                         extra: Union[discord.Message, bool, discord.VoiceChannel, str] = None):
        time = datetime.utcnow()
        try:
            guild_id = payload.guild.id
        except AttributeError:
            try:
                guild_id = payload.guild_id
            except AttributeError:
                guild_id = payload.data.get('guild_id')

        guild_conf = await self.bot.db.get_guild_config(guild_id)
        time += timedelta(hours=guild_conf.time_offset)
        time = time.strftime('%H:%M:%S')

        if raw:
            if mode == "bulk":
                await log.send(embed=discord.Embed(title="Bulk", description=f"Message ({payload.id}) has been {end}", timestamp=datetime.utcnow()))
            else:
                await log.send(embed=discord.Embed(title=f"Bulk", description=f"Message ({payload.message_id}) has been {end}", timestamp=datetime.utcnow()))
        else:
            if mode == "message_delete":
                try:
                    embed = discord.Embed(description=f"Message has been deleted in <#{payload.channel.id}>\n\n```{payload.content}```", timestamp=datetime.utcnow())
                    embed.set_author(name=payload.author, icon_url=payload.author.avatar_url)
                    await log.send(embed=embed)
                except discord.HTTPException:
                    embed = discord.Embed(description=f"Message has been deleted in <#{payload.channel.id}>\n\n```There was an error fetching the payload```", timestamp=datetime.utcnow())
                    embed.set_author(name=payload.author, icon_url=payload.author.avatar_url)
                    await log.send(embed=embed)
            elif mode == "message_edit":
                return #placeholder for later
            elif mode == "member_leave_vc":
                embed = discord.Embed(title="User left Voice", description=f"{payload} ({payload.id}) has left `{extra}`")
                await log.send(embed=embed)
            elif mode == "member_join_vc":
                embed = discord.Embed(title="User joined Voice", description=f"{payload} ({payload.id}) has joined `{extra}`")
                await log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        log_chn = await self.check_enabled(msg.guild.id, 'message_delete')
        if not log_chn:
            return
        await self.push_audit(log_chn, msg, False, mode='message_delete')


def setup(bot):
    bot.add_cog(Audit(bot))