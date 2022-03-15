### -- LAST EDITED BY DUNCAN TRUITT -- 11-14-2021 -- ###

### TO DO LIST ###
#
# 1. ADD LOGGING
# 2. CLEANUP
# 3. STUFF

import discord
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext import commands

import youtube_commands as yt
import os
import asyncio
from pytube import YouTube

import role_authenticator


client = commands.Bot(command_prefix='!')
role_auth = role_authenticator.Authenticator('auth_file.json')

@client.event
async def on_ready():
    print('Logged in as: {}'.format(client.user))
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='!help for commands'))
 


### --- LOAD COGS OR EXTENSIONS HERE --- ###

client.add_cog(yt.youtube_player(client))



### --- BASE COMMANDS GO HERE --- ####

@client.command()
async def ping(ctx):

    if role_auth.authenticate(ctx.guild.id, ctx.author.roles, 'ping'):
        await ctx.send('pong')
    else:
        await ctx.send("You do not have access to this command.")


@client.command()
async def pong(ctx):
    
    for role in ctx.author.roles:
        print(role.name)
    
    if role_auth.authenticate(ctx.guild.id, ctx.author.roles, 'pong'):
        await ctx.send('ping')
    else:
        await ctx.send("You do not have access to this command.")


@client.command()
async def roleadd(ctx, command, role):

    if role_auth.authenticate(ctx.guild.id, ctx.author.roles, 'roleadd'):
        role_auth.add_role(ctx.guild.id, role, command)
        await ctx.send(f'Giving {role} role permission to use {command}.')
    else:
        await ctx.send("You do not have access to this command.")




### --- RUN BOT --- NEED TO DEAL WITH HIDING TOKEN HERE --- ###

client.run('--- PUT TOKEN HERE ---')
