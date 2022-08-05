__author__ = "Joshua Burt"

import asyncio
import datetime
import sys
import time
import json
import discord

from os.path import exists
from colorama import Fore
from time import sleep
from discord.ext import commands

# Local Files
import json_utils
import roll as rl
import server as mcserver
import gamble

with open('json_files/config.json', 'r') as f:
    config = json.load(f)

# Constants
DISCORD_TOKEN = config["token"]
bot = discord.Bot()

points_loop = None


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    await log('Logged in as {0.user}'.format(bot) + Fore.YELLOW + '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)

    await json_utils.init()
    await gamble.init()

    global points_loop
    gamble.add_points.start(bot, config["voice_channel"], config["afk_channel"])


@bot.event
async def on_member_join(member):
    json_utils.add_user(member.id)


@bot.slash_command()
async def say(ctx, message):
    await ctx.respond(message)


@bot.message_command(name="mock")
async def mock(ctx, message: discord.Message):
    if message.author == bot.user:
        await ctx.respond('no')
    else:
        in_str = message.content
        await ctx.respond(await mockify(in_str))


@bot.slash_command()
async def mock(ctx):
    logs = await ctx.channel.history(limit=1).flatten()

    if logs[0].author == bot.user:
        await ctx.respond('no')
    else:
        in_str = logs[0].content
        await ctx.respond(await mockify(in_str))


@bot.command()
async def roll(ctx, input_string):
    await rl.roll(ctx, input_string)


@bot.slash_command(name="gamble")
async def bet(ctx, wager):
    if ctx.channel.id == config["gamble_channel"]:
        await gamble.gamble(ctx, bot, wager)

        author_id = ctx.message.author.id
        json_utils.update_user(author_id, "bets", json_utils.get_user_field(author_id, "bets") + 1)
    else:
        await ctx.respond("This isn't the gambling channel dummy")


@bot.slash_command(name="start", description="Start the Minecraft Server")
async def start_server(ctx):
    await log("Starting server...")
    await ctx.respond("Starting server...")
    await mcserver.start(ctx, bot, config["server_path"])

    game = discord.Game("Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.slash_command(name="stop", description="Stop the Minecraft Server")
async def stop_server(ctx):
    await mcserver.stop(ctx)


@bot.slash_command(name="intro", description="Toggle your intro when joining a voice call")
async def toggle_intro(ctx):
    new_play_on_enter = not json_utils.get_user_field(ctx.message.author.id, "play_on_enter")
    json_utils.update_user(ctx.message.author.id, "play_on_enter", new_play_on_enter)

    await ctx.respond(("Your intro is now ON" if new_play_on_enter else "Your intro is now OFF"))


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel and not member.bot:
        if json_utils.get_user_field(member.id, "play_on_enter") is None:
            return

        await play_sound(member, "downloads/intros/{}".format(json_utils.get_user_field(member.id, "file_name")))
        await log("Playing {}\'s{} intro in {}".format(Fore.YELLOW + member.name, Fore.WHITE,
                                                       Fore.YELLOW + after.channel.name + Fore.RESET))


@bot.command()
async def points(ctx):
    await gamble.points(ctx, bot)


@bot.command()
async def shop(ctx):
    with open('json_files/item_prices.json', 'r') as file:
        data = json.load(file)

        string = "Use **{} play *[Sound Name]*** to play the sound\n".format(config["prefix"])

        for row in data:
            string += "> Name: **{}** | Price: **{:,}**\n".format(row, data[row]["price"])

        await ctx.respond(string)


@bot.command(aliases=["play"])
async def pay_to_play(ctx, sound_name):
    current_points = json_utils.get_user_field(ctx.message.author.id, "points")
    cost = json_utils.get_sound_price(sound_name)

    if cost is None:
        await ctx.respond("There's no sound with that name ¯\\_(ツ)_/¯")
        return

    if current_points >= cost:
        json_utils.update_user(ctx.message.author.id, "points", current_points - cost)
        await play_sound(ctx.message.author, "downloads/pay_to_play/{}.mp3".format(sound_name))

        await log("Playing {}.mp3{}".format(Fore.YELLOW + sound_name, Fore.RESET))
    else:
        await ctx.respond("Aha you're poor. You're missing {:,} points".format(
            json_utils.get_sound_price(sound_name) - json_utils.get_user_field(ctx.message.author.id, "points")))


@bot.command(aliases=['give'])
async def pay(ctx, payee, amount):
    if len(payee) > 0 and len(amount) > 0 and int(amount) > 0:

        if json_utils.get_user_field(ctx.message.author.id, "points") > int(amount):
            await gamble.pay_points(ctx.message.author.id, payee.strip("<@>"), int(amount))
            await ctx.respond("**{}** paid **{}** - **{:,}** points".format(
                await gamble.get_user_from_id(bot, ctx.message.author.id),
                await gamble.get_user_from_id(bot, payee.strip("<@>")),
                amount))


@bot.command()
async def wan(ctx):
    await play_sound(ctx.message.author, "downloads/hello_there.mp3")


@bot.command()
@commands.is_owner()
async def restart(ctx):
    await log("Restarting...")
    sys.tracebacklimit = 0
    exit()


@bot.command()
@commands.is_owner()
async def reload(ctx):
    await log("Reloading JSON files...")
    await json_utils.reload_files()
    await log("Files reloaded")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # TODO: Inform user that the command doesn't exist
        return
    raise error


@bot.listen('on_message')
async def thanks(message):
    thank_you_messages = ['thanks obama', 'thank you obama', 'thx obama', 'tanks obama', 'ty obama', 'thank u obama']
    if any(x in message.content.lower() for x in thank_you_messages):
        await message.channel.respond(await json_utils.get_random_youre_welcome())


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


async def log(input_str):
    print(Fore.RESET + timestamp_to_readable(time.time()), Fore.WHITE + input_str)


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
