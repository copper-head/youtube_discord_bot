from discord.ext import commands
import help_msgs


@commands.command()
async def ping(ctx):
    await ctx.send("pong")

@commands.command()
async def list_commands(ctx, item='None'):
    await ctx.send(help_msgs.default_help)

def setup(client):
    client.add_command(ping)
    client.add_command(list_commands)