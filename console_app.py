import os

import asyncio
import string
import aioconsole
from discord.ext import commands


class ConsoleApp:

    def __init__(self, client: commands.Bot):

        self.client = client

    # A loop function that is run by a client task
    async def run(self):

        await self.client.wait_until_ready()

        self.bot_running = True

        # Main loop
        while self.bot_running:

            console_input = await aioconsole.ainput("yt_bot>>>")   # Get Console Input
            await self.parse_command(console_input)          # Pass input into parse_command() to be handled


    async def parse_command(self, command: string):

        # Takes strings and sees if their a command.
        # This is not a very good implementation.

        if command == "stop":
            self.bot_running = False
            await aioconsole.aprint("Stopping Bot...")
            await self.stop_bot()
        if command == "voicecount":
            await self.voice_client_count()
        if command == "clearcache":
            await self.clear_yt_cache()


    # Gracefully shuts down the bot.
    async def stop_bot(self):

        # Disconnect voice clients
        for vc in self.client.voice_clients:
            await vc.disconnect()

        await self.client.close()


    # Print number of active voice clients
    async def voice_client_count(self):

        string_message = "Active Voice Clients Count: " + str(len(self.client.voice_clients))
        await aioconsole.aprint(string_message)

    # Clears youtube cache (yt_source folder)
    async def clear_yt_cache(self):

        yt_source_path = "yt_source"

        file_del_count = 0
        bytes_del_count = 0
        for f in os.listdir(yt_source_path):
            f_path = "{}/{}".format(yt_source_path, f)
            bytes_del_count += os.path.getsize(f_path)
            file_del_count += 1

            try:
                os.remove(f_path)
            except PermissionError:
                bytes_del_count -= os.path.getsize(f_path)
                file_del_count -= 1

        string_message = "{} files deleted. Freed {} bytes.".format(file_del_count, bytes_del_count)
        await aioconsole.aprint(string_message)
