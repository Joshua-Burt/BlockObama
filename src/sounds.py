import asyncio
import json
from os.path import exists

import discord
from colorama import Fore
from discord import option
from mutagen.mp3 import MP3

from bot import bot
from log import log
import json_utils

sound_queue = []
sound_list = []


async def init():
    global sound_list

    with open('../json_files/item_prices.json', 'r') as file:
        sound_list = json.load(file)


@bot.slash_command(name="shop", description="Display the sounds shop")
async def shop(ctx):
    string = "Use **/play *[Sound Name]*** to play the sound\n"

    for sound_name in sound_list:
        string += f"> Name: **{sound_name}** | Price: **{sound_list[sound_name]['price']:,}**\n"

    await ctx.respond(string)


@bot.slash_command(name="play", description="Play a sound")
@option(
    "sound_name",
    description="Name of the sound from the shop",
    required=True,
    default=""
)
async def pay_to_play(ctx, sound_name):
    current_points = json_utils.get_user_field(ctx.author.id, "points")
    cost = json_utils.get_sound_price(sound_name)

    if cost is None:
        await ctx.respond("There's no sound with that name ¯\\_(ツ)_/¯")
        return

    if current_points >= cost:
        await ctx.respond(f"Playing {sound_name}.mp3")
        await log(f"Playing {Fore.YELLOW + sound_name}.mp3{Fore.RESET}")

        await play_sound(ctx.author, f"../sounds/shop_sounds/{sound_name}.mp3")

        json_utils.update_user(ctx.author.id, "points", current_points - cost)
    else:
        await ctx.respond("Aha you're poor. You're missing {:,} points".format(
            json_utils.get_sound_price(sound_name) - json_utils.get_user_field(ctx.author.id, "points")))


async def play_sound(member: discord.Member, sound_path):
    if exists(sound_path):
        voice_channel = member.voice.channel

        # Verify the user is in a voice channel
        if not voice_channel:
            return

        sound_queue.append(sound_path)

        # Check if the bot is not already in a voice channel
        if bot.user in voice_channel.members:
            return

        try:
            voice = await voice_channel.connect()
        except discord.errors.ClientException:
            # The client already is in a channel
            # Run through each voice channel and disconnect from which ever is connected
            for i in range(len(bot.voice_clients)):
                if bot.voice_clients[i].guild == member.guild:
                    await bot.voice_clients[i].disconnect()
                    break

            # Reconnect to the new channel after disconnecting from the previous
            voice = await voice_channel.connect()

        while len(sound_queue) > 0:
            source = sound_queue.pop(0)
            audio_length = MP3(source).info.length
            voice.play(discord.FFmpegPCMAudio(executable="../ffmpeg/bin/ffmpeg.exe", source=source))

            voice.pause()
            await asyncio.sleep(0.5)
            voice.resume()

            await asyncio.sleep(audio_length + 2)

        await voice.disconnect(force=True)