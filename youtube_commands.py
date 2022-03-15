## -- TO DO -- ##
#
# 2. Add Error handling to make sure url is valid
# 4. Add garbage collection - ie delete videos that are not being played anymore


import discord
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext import commands
import os
import asyncio
from pytube import YouTube
import pytube
import role_authenticator



role_auth = role_authenticator.Authenticator('auth_file.json')

# Youtube player Cog for playing youtube video audio through voice channels

class youtube_player(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queues = {}
    
    
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
        except pytube.exceptions.RegexMatchError:
            await ctx.send("Sorry, but {} does not appear to be valid :(".format(url))
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
                    print('Not connected to a channel')
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
            Descrip: Resumes voice client in voice channel of the sending user.

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
            Descrip: Skips current video being played and plays next video in queue if available.

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
            Descrip: Stops playing and disconnects voice client - deletes video queue as well.

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

        channel_id = ctx.author.voice.channel.id

        i = 1
        for url in self.queues[channel_id]:
            yt = YouTube(url)
            row = "{}. ".format(i) + yt.title
            await ctx.send(row)
            i += 1

