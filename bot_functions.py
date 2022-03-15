import discord
from discord.ext import commands

@commands.command()
async def ping(ctx):
    await ctx.send("pong")

def setup(client):
    client.add_command(ping)