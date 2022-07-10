import datetime
import time
from os.path import exists

from colorama import Fore, Back
from time import sleep
from discord.ext import commands

import discord

import roll as rl
import server as mcserver
import gamble
import json

# Constants
DISCORD_TOKEN = 'Nzk3NjUxNTc0OTQ3MTg0NzEw.X_pk6w.uO-sRng69YLuWrIBDEr9KHNLDfY'
DAVID_ID = 416415708323512341
MORGAN_ID = 429659989750317076
QUINN_ID = 325111288764170240
JACOB_ID = 416415943896596493
AUSTIN_ID = 253305173118550026
BEN_ID = 349986879615008778
JOSH_ID = 382324502199271424
NOAH_ID = 196360954160742400
ID_LIST = [DAVID_ID, MORGAN_ID, QUINN_ID, JACOB_ID, AUSTIN_ID, BEN_ID, JOSH_ID, NOAH_ID]

global json_file

bot = commands.Bot(command_prefix="!ob ")


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    log('Logged in as {0.user}'.format(bot) + Fore.YELLOW +
        '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)

    with open('settings.json', 'r') as f:
        data = json.load(f)

    global json_file
    json_file = data

    bot.loop.create_task(gamble.add_points(bot, update_json, json_file))


@bot.command(pass_context=True)
async def say(ctx, message):
    await ctx.message.delete()
    await ctx.send(message)


@bot.command()
async def mock(ctx):
    logs = await ctx.channel.history(limit=2).flatten()

    if logs[1].author == bot.user:
        await ctx.send('no')
    else:
        in_str = logs[1].content
        await ctx.send(await mockify(in_str))


@bot.command()
async def roll(ctx, input_string):
    await rl.roll(ctx, input_string)


@bot.command(aliases=["gamble"])
async def bet(ctx, wager):
    if ctx.channel.id == 993918882228207717:
        await gamble.gamble(ctx, bot, wager, json_file, update_json, ID_LIST)
        update_json(str(ctx.message.author.id), "bets", json_file[str(ctx.message.author.id)]["bets"] + 1)


@bot.command()
async def start(ctx):
    log("Starting server...")
    await ctx.send("Starting server...")
    await mcserver.start(ctx, bot)


@bot.command(name='intro', description='Toggle intro on entering voice chat')
async def toggle_intro(ctx):
    if str(ctx.message.author.id) not in json_file:
        ctx.send("You don't have an intro at the moment")
        return

    new_play_on_enter = not json_file[str(ctx.message.author.id)]["play_on_enter"]

    update_json(ctx.message.author.id, "play_on_enter", new_play_on_enter)

    await ctx.send(("Your intro is now ON" if new_play_on_enter else "Your intro is now OFF"))


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel and not member.bot:

        json_member = json_file[str(member.id)]
        if json_member is not None:
            if not json_member["play_on_enter"]:
                return

            await play_sound(member, "downloads/{}".format(json_member["file_name"]))


@bot.command(aliases=["points"])
async def say_points(ctx):
    await gamble.points(ctx, bot, json_file, ID_LIST)


# Helper functions

# Take the last message sent and repeats it with alternating capitals
# e.g. "Spongebob" -> "SpOnGeBoB"
async def mockify(in_str):
    new_string = ""
    case = True  # true = uppercase, false = lowercase

    for i in in_str:
        if case:
            new_string += i.upper()
        else:
            new_string += i.lower()
        if i != ' ':
            case = not case
    return new_string


def timestamp_to_readable(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S -')


def log(input_str):
    print(Fore.RESET + timestamp_to_readable(time.time()), Fore.WHITE + input_str)


def update_json(member_id, field, value):
    global json_file
    json_member = json_file[str(member_id)]

    if json_member is not None:
        json_file[str(member_id)][field] = value

        # Dump into file
        with open('settings.json', 'w') as f:
            json.dump(json_file, f, indent=4)


async def play_sound(member, source):
    if exists(source):
        singing_channel = member.voice.channel
        await singing_channel.connect()

        log("Playing {}\'s{} intro in {}".format(Fore.YELLOW + member.name, Fore.WHITE, Fore.YELLOW + singing_channel.name + Fore.RESET))

        bot.voice_clients[0].play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=source))

        sleep(5)

        await bot.voice_clients[0].disconnect()

bot.run(DISCORD_TOKEN)
