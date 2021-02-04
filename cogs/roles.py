import discord

from discord.ext import commands

from core.utility import EmojiOrUnicode, tryint


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["reaction-role"], invoke_without_command=True)
    async def reactionrole(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @reactionrole.command(name='add')
    async def rr_add(self, ctx, channel: discord.TextChannel, message_id: int, emoji: EmojiOrUnicode,
                     role: discord.Role):
        """Add an emoji to a role"""
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.author.owner.id:
            return await ctx.send("User does not have permission")

        try:
            msg = await channel.fetch_message(message_id)
        except discord.NotFound:
            return await ctx.send("That message ID was invalid or cannot be found.")

        try:
            reaction = f'reaction_role: {int(emoji.id)}'
        except ValueError:
            reaction = emoji.id
        await msg.add_reaction(reaction)

        await self.bot.db.update_guild_config(ctx.guild.id, {'$addToSet': {'reaction_roles': {
            'message_id': str(message_id),
            'emoji_id': str(emoji.id),
            'role_id': str(role.id)
        }}})

        await ctx.send("Completed!")

    @reactionrole.command(name="remove")
    async def rr_remove(self, ctx, message_id: int, role: discord.Role) -> None:
        """Remove an emoji from reaction roles"""
        try:
            role_info = (await self.bot.db.get_guild_config(ctx.guild.id)).reaction_roles.get_kv('message_id',
                                                                                                 str(message_id))
        except IndexError:
            return await ctx.send("There was an error fetching that message.")

        await self.bot.db.update_guild_config(ctx.guild.id, {'$pull': {'reaction_roles': role_info}})
        await ctx.send("Completed!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Add reaction roles"""
        reaction_roles = (await self.bot.db.get_guild_config(payload.guild_id)).reaction_roles
        emoji_id = payload.emoji.id or str(payload.emoji)
        msg_roles = list(filter(lambda r: int(r.message_id) == payload.message_id and tryint(r.emoji_id) == emoji_id,
                                reaction_roles))

        if msg_roles:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(msg_roles[0].role_id))

            await member.add_roles(role, reason='Reaction Role')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Remove reaction roles"""
        reaction_roles = (await self.bot.db.get_guild_config(payload.guild_id)).reaction_roles
        emoji_id = payload.emoji.id or str(payload.emoji)
        msg_roles = list(filter(lambda r: int(r.message_id) == payload.message_id and tryint(r.emoji_id) == emoji_id,
                                reaction_roles))

        if len(msg_roles) == 1:
            guild = self.bot.get_guild(int(payload.guild_id))
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(msg_roles[0].role_id))

            await member.remove_roles(role, reason='Reaction Role')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        """Removes any autoroles, selfroles, or reaction roles that are deleted"""
        guild_config = await self.bot.db.get_guild_config(role.guild.id)
        db_keys = ['selfroles', 'autoroles', 'reaction_roles']
        for k in db_keys:
            if str(role.id) in getattr(guild_config, k):
                await self.bot.db.update_guild_config(role.guild.id, {'$pull': {k: str(role.id)}})


def setup(bot):
    bot.add_cog(Roles(bot))
