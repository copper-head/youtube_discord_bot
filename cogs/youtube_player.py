# ---- AUTHOR: DUNCAN TRUITT ---- #
# ---- LAST EDITED: 7/9/2022 ---- #
# -- YOUTUBE PLAYER DISCORD COG - #

# ==== TO DO ==== #
# 1. Define Constants in the cog itself.
# 2. Handle any db exceptions.

### ====== EXTERNAL IMPORTS ====== ###
import discord
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext import commands, tasks
import os
import asyncio
from pytube import YouTube
import pytube

### ======== LOCAL IMPORTS ======== ###
from constants import *
import db.interface as db


class youtube_player(commands.Cog):

    '''
        Description:
            This cog adds commands for a discord bot to be able to play
            youtube videos through discord voice channels.
        
        Discord Commands: !play, !pause, !resume, !skip, !stop

        Notes:
            - *** THIS COG REQUIRES ffmpeg TO BE INSTALLED IN ORDER TO FUNCTION. ***

            - Currently the bot REQUIRES the local imports in order to function
            without throwing any exceptions. I need to edit this to where it
            only throws warnings as opposed to throwing exceptions and crashing
            the bot.

            - There is also an existing issue with pytube that requires some
            modification of the library itself in order for it to work properly.
            This is an issue with pytube, and not the cog.
    '''

    def __init__(self, client):
        self.client = client
        self.queues = {}

        # To be implemented
        self.not_in_channel_message = ""

        # Start cache cleanup bg task
        self.cleanup_yt_cache.start()

    @commands.command()
    async def play(self, ctx, url):


        '''
        Plays a youtube video through channel based on URL and creates a queue for the channel.
        If another video is playing then the url is appended to the channel's queue.

        :param url: -- Youtube URL
        :return:
        '''

        if ctx.author.voice == None:
            await ctx.send("You must be in a voice channel to use that command.")
            return

        # Get voice channel ID
        channel_id = ctx.author.voice.channel.id

        # Check to make sure URL is valid
        try:
            yt = YouTube(url)
        except pytube.exceptions.VideoUnavailable:
            await ctx.send(f"{url} is unavaliable.")
            return
        except pytube.exceptions.PytubeError:
            await ctx.send(f"An error occured when trying to fetch {url}.")
            return

        # If a video queue doesn't exist for this channel already, create one.
        if channel_id not in self.queues:

            self.queues[channel_id] = [url]
            await ctx.send("Playing {}".format(url))

            # Get voice channel that the user is in
            channel = ctx.author.voice.channel

            # Runs until the queue is empty and last video is played
            playing = True
            while playing:

                # Get next url in queue
                yt = YouTube(self.queues[channel_id].pop(0))

                # Get yt stream and download
                stream = yt.streams.get_by_itag(18)
                stream.download(output_path='yt_source', filename="{}.mp4".format(yt.video_id))

                # Wait until file is downloaded
                while os.path.exists('yt_source/{}.mp4'.format(yt.video_id)) == False:
                    await asyncio.sleep(2)

                # Create voice client and join channel
                if channel != None:
                    try:
                        voice = get(self.client.voice_clients, guild=ctx.guild)
                        voice = await channel.connect()
                    except discord.client.ClientException:
                        print("ClientException occurred. Ignoring.")

                    # Start playing
                    source = FFmpegPCMAudio('yt_source/{}.mp4'.format(yt.video_id))
                    voice.play(source)
                else:
                    print('Must be connected to a voice channel to use this command.')
                    return

                # Wait while video is played
                while voice.is_playing() or voice.is_paused():
                    await asyncio.sleep(5)

                # Checks to see if queue is empty after current video is done playing.
                if len(self.queues[channel_id]) == 0:
                    playing = False

            await voice.disconnect()

            #channel = ctx.author.voice.channel

            # Delete queue from queue dict when playing is complete
            self.queues.pop(channel_id, None)

        else:
            # Adds URL to queue if queue already exists
            await ctx.send("Added {} to queue.".format(url))
            self.queues[channel_id].append(url)


    @commands.command()
    async def pause(self, ctx):
        '''
            Descrip: Pauses voice client in voice channel of the sending user.
        '''

        if ctx.author.voice == None:
            await ctx.send("You must be in a voice channel to use that command.")
            return

        await ctx.send("Paused")

        channel = ctx.author.voice.channel

        if channel != None:
            voice = get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                voice.pause()
        else:
            await ctx.send("You must be in a voice channel to use that command.")
            return


    @commands.command()
    async def resume(self, ctx):
        '''
            Resumes voice client in voice channel of the sending user.
        '''

        if ctx.author.voice == None:
            await ctx.send("You must be in a voice channel to use that command.")
            return

        await ctx.send("Resuming")
        channel = ctx.author.voice.channel

        if channel != None:
            voice = get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
        else:
            await ctx.send("You must be in a voice channel to use that command.")
            return


    @commands.command()
    async def skip(self, ctx):

        '''
            Skips current video being played and plays next video in queue if available.
        '''

        if ctx.author.voice == None:
            await ctx.send("You must be in a voice channel to use that command.")
            return

        await ctx.send("Skipping")
        channel = ctx.author.voice.channel

        if channel != None:
            voice = get(self.client.voice_clients, guild=ctx.guild)
            voice.stop()
        else:
            await ctx.send("You must be in a voice channel to use that command.")
            return


    @commands.command()
    async def stop(self, ctx):

        '''
            Stops playing and disconnects voice client - deletes video queue as well.
        '''

        if ctx.author.voice == None:
            await ctx.send("You must be in a voice channel to use that command.")
            return

        await ctx.send("Stopping")
        channel = ctx.author.voice.channel
        channel_id = ctx.author.voice.channel.id

        if channel != None:
            voice = get(self.client.voice_clients, guild=ctx.guild)
            self.queues[channel_id].clear()
            voice.stop()
        else:
            await ctx.send("You must be in a voice channel to use that command.")
            return

    @commands.command()
    async def queue(self, ctx):

        '''
            Not exactly sure what this is, needs work or needs to be removed.
        '''

        channel_id = ctx.author.voice.channel.id

        i = 1
        for url in self.queues[channel_id]:
            yt = YouTube(url)
            row = "{}. ".format(i) + yt.title
            await ctx.send(row)
            i += 1
    
    @tasks.loop(minutes=YT_SOURCE_CHECK_INTERVAL)
    async def cleanup_yt_cache(self):
        
        '''
            Background loop that checks to see if cache folder needs cleared.
            If YT_SOURCE_MAX_SIZE is reached, the task will delete all the files in the folder.
        '''

        file_count = 0
        bytes_count = 0

        # Get number of files and size of YT_SOURCE_PATH
        for f in os.listdir(YT_SOURCE_PATH):
            f_path = "{}/{}".format(YT_SOURCE_PATH, f)
            bytes_count += os.path.getsize(f_path)
            file_count += 1
        
        # If YT_SOURCE_PATH max size threshold is reached, delete files in directory.
        if bytes_count > YT_SOURCE_MAX_SIZE * 1024 * 1024:
            
            bytes_del_count = 0 # Number of bytes deleted
            file_del_count = 0  # Number of files deleted
            bytes_not_del = 0   # Number of bytes that task was unable to delete
            file_not_del = 0    # Number of files that task was unable to delete

            # Delete Files in the source path
            for f in os.listdir(YT_SOURCE_PATH):
                f_path = "{}/{}".format(YT_SOURCE_PATH, f)
                bytes_del_count += os.path.getsize(f_path)
                file_del_count += 1
            
                try:
                    os.remove(f_path)
                except Exception as e:
                    bytes_del_count -= os.path.getsize(f_path)
                    file_del_count -= 1
                    bytes_not_del += os.path.getsize(f_path)
                    file_not_del += 1
            
            final_b_count = 0   # Number of bytes AFTER deleting
            final_f_count = 0   # Number of files AFTER deleting

            # Get size of path after deletion.
            for f in os.listdir(YT_SOURCE_PATH):
                f_path = "{}/{}".format(YT_SOURCE_PATH, f)
                final_b_count += os.path.getsize(f_path)
                final_f_count += 1

            # Log event here
            if final_b_count > YT_SOURCE_WARNING_THRESHOLD * 1048576:
                db.log_event("WARNING", "YT Cache Clear Warning", "Youtube Cache Size above threshold after attempting to clear. Folder Size: {} MB".format(final_b_count / 1048576))
            elif final_b_count > YT_SOURCE_CRITICAL_THRESHOLD * 1048576:
                db.log_event("CRITICAL", "YT Cache Clear CRITICAL", "Youtube Cache Size above threshold after attempting to clear. Folder Size: {} MB".format(final_b_count / 1048576))
            else:
                db.log_event("INFO", "YT Cache Clear", f"Deleted {file_del_count} file(s) ({(bytes_del_count / 1048576):.1f} MB) from {YT_SOURCE_PATH}.")