# Author: Duncan Truitt
#
# Youtube discord bot.

import discord
from discord.ext import commands
import console_app
import cogs.youtube_player as yt
import base_functions
import db.interface as db


### ============== INIT DATABASE AND CREATE CLIENT ============== ###

db.init_db()
client = commands.Bot(command_prefix='!')


### ============== CLIENT EVENTS ============== ###

@client.event
async def on_ready():
    print('Logged in as: {}'.format(client.user))
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='!help for commands'))

# Adds a log to DB whenever a command is called.
@client.event
async def on_command(ctx):
    db.log_command_call(ctx.command.name, ctx)




### --- LOAD COGS OR EXTENSIONS HERE --- ###
client.add_cog(yt.youtube_player(client))
base_functions.setup(client)


### --- CONSOLE INTERFACE --- ###
c_app = console_app.ConsoleApp(client)

### --- RUN BOT --- NEED TO DEAL WITH HIDING TOKEN HERE --- ###
client.loop.create_task(c_app.run())
client.run('OTUzMTA1NDUxMjE2Njc0ODg3.Yi_unw.DcYAHPqO_PUWiTzj9tW3KtPGQ0Q')
