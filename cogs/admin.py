import discord

from discord.ext import commands


class AdminConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

