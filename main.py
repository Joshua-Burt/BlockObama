import asyncio
import datetime
import os
import sys
import time
from os.path import exists

from colorama import Fore
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
global price_file
points_loop = None

bot = commands.Bot(command_prefix="!ob ")


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    log('Logged in as {0.user}'.format(bot) + Fore.YELLOW +
        '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)

    with open('users.json', 'r') as f:
        user_data = json.load(f)

    with open('item_prices.json', 'r') as f:
        price_data = json.load(f)

    global json_file
    json_file = user_data

    global price_file
    price_file = price_data

    await gamble.init()

    global points_loop
    points_loop = bot.loop.create_task(gamble.add_points(bot, update_json, json_file))

    gamble.add_points.start(bot, update_json, json_file)


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


@bot.command(aliases=['start server', 'start'])
async def start_server(ctx):
    log("Starting server...")
    await ctx.send("Starting server...")
    await mcserver.start(ctx, bot)


@bot.command(aliases=['stop server', 'stop'])
async def stop_server(ctx):
    await mcserver.stop(ctx)


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
            log("Playing {}\'s{} intro in {}".format(Fore.YELLOW + member.name, Fore.WHITE,
                                                     Fore.YELLOW + after.channel.name + Fore.RESET))


@bot.command(aliases=["points"])
async def say_points(ctx):
    await gamble.points(ctx, bot, json_file, ID_LIST)


@bot.command()
async def shop(ctx):
    with open('item_prices.json', 'r') as f:
        data = json.load(f)

        string = "Use *!ob play {Song Name}* to play the sound\n"

        for row in data:
            string += "> Name: **{}** | Price: **{}**\n".format(row, data[row]["price"])

        await ctx.send(string)


@bot.command(aliases=["play"])
async def pay_to_play(ctx, sound_name):
    current_points = get_json(ctx.message.author.id, "points")
    cost = get_sound_price(sound_name)

    if current_points >= cost:
        update_json(ctx.message.author.id, "points", current_points - cost)
        await play_sound(ctx.message.author, "downloads/pay_to_play/{}.mp3".format(sound_name))

        log("Playing {}.mp3{}".format(Fore.YELLOW + sound_name, Fore.RESET))
    else:
        await ctx.send("Aha you're poor. You're missing {} points".format(
            get_sound_price(sound_name) - get_json(ctx.message.author.id, "points")))


@bot.command(aliases=['give'])
async def pay(ctx, payee, amount):
    if len(payee) > 0 and len(amount) > 0 and int(amount) > 0:

        if get_json(ctx.message.author.id, "points") > int(amount):
            await gamble.pay_points(ctx.message.author.id, payee.strip("<@>"), int(amount), json_file, update_json)
            await ctx.send(
                "**{}** paid **{}** - **{}** points".format(
                    await gamble.get_user_from_id(bot, ctx.message.author.id),
                    await gamble.get_user_from_id(bot, payee.strip("<@>")),
                    amount))


@bot.command()
async def wan(ctx):
    await play_sound(ctx.message.author, "downloads/hello_there.mp3")


@bot.command()
@commands.is_owner()
async def restart(ctx):
    # await bot.close()
    log("Restarting...")
    sys.tracebacklimit = 0
    exit()
    # os.execv(sys.executable, ['py3'] + sys.argv)


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
        with open('users.json', 'w') as f:
            json.dump(json_file, f, indent=4)


def get_json(member_id, field):
    global json_file
    json_member = json_file[str(member_id)]

    if json_member is not None:
        return json_member[field]
    return None


def get_sound_price(sound_name):
    return price_file[sound_name]["price"]


async def play_sound(member, source):
    if exists(source):
        singing_channel = member.voice.channel

        if singing_channel:
            await singing_channel.connect()

            voice = bot.voice_clients[0]
            voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=source))

            voice.pause()
            await asyncio.sleep(0.5)
            voice.resume()

            sleep(5)

            await bot.voice_clients[0].disconnect()


bot.run(DISCORD_TOKEN)
