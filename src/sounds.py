import asyncio
import json
from os.path import exists

import discord
from colorama import Fore
from discord import option
from mutagen.mp3 import MP3

from bot import bot
from log import log
from json_utils import update_user, get_sound_price, get_user_field

is_playing = False
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
    current_points = await get_user_field(ctx.author.id, "points")
    cost = await get_sound_price(sound_name)

    if cost is None:
        await ctx.respond("There's no sound with that name ¯\\_(ツ)_/¯")
        return

    if current_points >= cost:
        await ctx.respond(f"Playing {sound_name}.mp3")
        await log(f"Playing {Fore.YELLOW + sound_name}.mp3{Fore.RESET}")

        await add_to_queue(ctx.author, f"../sounds/shop_sounds/{sound_name}.mp3")

        await update_user(ctx.author.id, "points", current_points - cost)
    else:
        await ctx.respond("Aha you're poor. You're missing {:,} points".format(
            await get_sound_price(sound_name) - await get_user_field(ctx.author.id, "points")))


async def play_queue():
    global is_playing
    is_playing = True

    while len(sound_queue) > 0:
        sound_dict = sound_queue.pop(0)
        voice = await play_sound(sound_dict)

        # Disconnect from the voice channel is there are no more sounds to play
        if len(sound_queue) == 0:
            await voice.disconnect()
            break

        # Disconnect from the voice channel if the next sound isn't in the same channel
        if sound_dict["channel"] != sound_queue[0]["channel"]:
            await voice.disconnect()

    is_playing = False


async def play_sound(sound_dict):
    path = sound_dict["path"]
    if not exists(path):
        return

    voice_channel = sound_dict["channel"]
    if not voice_channel:
        return

    voice = await sound_dict["channel"].connect()

    # Stay in this channel as long as the next sound is in the same channel
    while True:
        file_name = sound_dict['path'][sound_dict['path'].rfind('/') + 1:]

        await log("Playing {} in {}".format(Fore.YELLOW + file_name + Fore.WHITE, Fore.YELLOW + sound_dict['channel'].name + Fore.RESET))

        audio_length = MP3(path).info.length
        voice.play(discord.FFmpegPCMAudio(executable="../ffmpeg/bin/ffmpeg.exe", source=path))

        voice.pause()
        await asyncio.sleep(0.5)
        voice.resume()

        await asyncio.sleep(audio_length + 2)

        # Break from the loop if there's no sounds
        if len(sound_queue) == 0:
            break

        # Change the path to the next sound if they are contained within the same channel
        if sound_queue[0]["channel"] == sound_dict["channel"]:
            path = sound_queue.pop()["path"]
        else:
            break

    return voice


async def add_to_queue(member: discord.Member, sound_path):
    sound_queue.append({"channel": member.voice.channel, "path": sound_path})
    if not is_playing:
        await play_queue()