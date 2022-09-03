__author__ = "Joshua Burt"

import asyncio
import datetime
import time
import json
import discord

from os.path import exists

from mutagen.mp3 import MP3
from colorama import Fore
from discord import option
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
sound_queue = []


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    await log('Logged in as {0.user}'.format(bot) + Fore.YELLOW + '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)

    await json_utils.init()
    await gamble.init()

    # Loop used to check if members are in voice channels
    global points_loop
    gamble.add_points.start(bot, config["voice_channel"], config["afk_channel"])


@bot.event
async def on_member_join(member):
    await log("Adding member {}".format(member))
    json_utils.add_user(member.id)


@bot.slash_command(name="say", description="Repeat the inputted message")
async def say(ctx, message):
    await ctx.send(message)
    await ctx.respond("Said the words", ephemeral=True)


@bot.message_command(name="mock", description="Mock the selected message")
async def mock(ctx, message: discord.Message):
    if message.author == bot.user:
        await ctx.respond('no')
    else:
        in_str = message.content
        await ctx.respond(await mockify(in_str))


@bot.slash_command(name="mock", description="Mock the last message sent")
async def mock(ctx):
    # Retrieves the last message sent in the channel
    logs = await ctx.channel.history(limit=1).flatten()

    if logs[0].author == bot.user:
        await ctx.respond('no')
    else:
        in_str = logs[0].content
        await ctx.respond(await mockify(in_str))


@bot.slash_command(name="roll", description="Roll a number of various sided dice")
@option(
    "modifier",
    description="How much to add/subtract from the total roll",
    required=False,
    default=0
)
async def roll(ctx, number_of_dice, number_of_faces, modifier):
    # Formatting depending on the value of modifier
    if int(modifier) >= 0:
        roll_str = "{}d{} + {}".format(number_of_dice, number_of_faces, modifier)
    else:
        roll_str = "{}d{} - {}".format(number_of_dice, number_of_faces, abs(int(modifier)))

    await rl.roll(ctx, roll_str)


@bot.slash_command(name="gamble")
async def bet(ctx, wager):
    if ctx.channel.id == config["gamble_channel"]:
        await gamble.gamble(ctx, bot, wager)

        author_id = ctx.author.id
        json_utils.update_user(author_id, "bets", json_utils.get_user_field(author_id, "bets") + 1)
    else:
        await ctx.respond("This isn't the gambling channel dummy")


@bot.slash_command(name="start", description="Start the Minecraft Server")
async def start_server(ctx):
    await log("Starting server...")
    await mcserver.start(ctx, config["server_path"])

    # Display that server is running
    game = discord.Game("Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.slash_command(name="stop", description="Stop the Minecraft Server")
async def stop_server(ctx):
    await log("Stopped the server")
    await mcserver.stop(ctx)

    # Display that server isn't running
    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.slash_command(name="intro", description="Toggle your intro when joining a voice call")
async def toggle_intro(ctx):
    # Get and set the opposite current play_on_enter value
    new_play_on_enter = not json_utils.get_user_field(ctx.author.id, "play_on_enter")
    json_utils.update_user(ctx.author.id, "play_on_enter", new_play_on_enter)

    await ctx.respond(("Your intro is now ON" if new_play_on_enter else "Your intro is now OFF"))


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel and not member.bot:
        if json_utils.get_user_field(member.id, "play_on_enter") is None:
            return

        await log("Playing {}\'s{} intro in {}".format(Fore.YELLOW + member.name, Fore.WHITE,
                                                       Fore.YELLOW + after.channel.name + Fore.RESET))
        await play_sound(member, "downloads/intros/{}".format(json_utils.get_user_field(member.id, "file_name")))


@bot.slash_command(name="points", description="Display the points of each member")
async def points(ctx):
    await gamble.points(ctx, bot)


@bot.slash_command(name="shop", description="Display the sounds shop")
async def shop(ctx):
    with open('json_files/item_prices.json', 'r') as file:
        data = json.load(file)

        string = "Use **/play *[Sound Name]*** to play the sound\n"

        for row in data:
            string += "> Name: **{}** | Price: **{:,}**\n".format(row, data[row]["price"])

        await ctx.respond(string)


@bot.slash_command(name="play", description="Play a sound")
async def pay_to_play(ctx, sound_name):
    current_points = json_utils.get_user_field(ctx.author.id, "points")
    cost = json_utils.get_sound_price(sound_name)

    if cost is None:
        await ctx.respond("There's no sound with that name ¯\\_(ツ)_/¯")
        return

    if current_points >= cost:
        await ctx.respond("Playing {}.mp3".format(sound_name))
        await log("Playing {}.mp3{}".format(Fore.YELLOW + sound_name, Fore.RESET))

        await play_sound(ctx.author, "downloads/pay_to_play/{}.mp3".format(sound_name))

        json_utils.update_user(ctx.author.id, "points", current_points - cost)
    else:
        await ctx.respond("Aha you're poor. You're missing {:,} points".format(
            json_utils.get_sound_price(sound_name) - json_utils.get_user_field(ctx.author.id, "points")))


@bot.slash_command(name="pay", description="Pay amount of points to another user")
async def pay(ctx, payee, amount):
    if len(payee) > 0 and len(amount) > 0 and int(amount) > 0:
        if json_utils.get_user_field(ctx.author.id, "points") > int(amount):
            await gamble.pay_points(ctx.author.id, payee.strip("<@!>"), int(amount))

            await ctx.respond("**{}** paid **{}** - **{:,}** points".format(
                await gamble.get_user_from_id(bot, ctx.author.id),
                await gamble.get_user_from_id(bot, payee.strip("<@!>")), int(amount)))


@bot.slash_command(name="nick", description="Change the nickname of a user")
async def nick(ctx, username, new_nick):
    if len(username) > 0 and len(new_nick) > 0:
        user = await ctx.guild.fetch_member(username.strip("<@!>"))
        await user.edit(nick=new_nick)
        await ctx.respond("Changed {}'s nickname to {}".format(user.name, new_nick), ephemeral=True)


@bot.slash_command(name="wan", description="Hello there")
async def wan(ctx):
    await ctx.respond("Hello there")
    await play_sound(ctx.author, "downloads/hello_there.mp3")


@bot.slash_command(name="reload", description="Reloads the bot's internal files")
@commands.is_owner()
async def reload(ctx):
    await ctx.respond("Reloading...")
    await log("Reloading JSON files...")
    await json_utils.reload_files()
    await log("Files reloaded")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        ctx.respond("That command doesn't exist", ephemeral=True)
        return
    raise error


@bot.listen('on_message')
async def thanks(message):
    # Anytime one of the below "Thanks"s gets messaged, the bot will reply with a random response
    thank_you_messages = ['thanks obama', 'thank you obama', 'thx obama', 'tanks obama', 'ty obama', 'thank u obama']
    if any(x in message.content.lower() for x in thank_you_messages):
        await message.channel.respond(await json_utils.get_random_youre_welcome())


# Helper functions

# Take the last message sent and repeats it with alternating capitals
# e.g. "Spongebob" -> "SpOnGeBoB"
async def mockify(in_str):
    new_string = ""
    case = True  # True = uppercase, False = lowercase

    for i in in_str:
        new_string += i.upper() if case else i.lower()

        if i != ' ':
            case = not case

    return new_string


def timestamp_to_readable(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S -')


async def log(input_str):
    print(Fore.RESET + timestamp_to_readable(time.time()), Fore.WHITE + input_str)


async def play_sound(member: discord.Member, source_name):
    if exists(source_name):
        # Get the voice channel the member is currently in
        channel = member.voice.channel
        sound_queue.append(source_name)

        # Verify channel exists, and that the bot isn't already in the channel
        if channel and bot.user not in channel.members:
            voice = await channel.connect()

            # Keep playing the sounds until the queue is empty
            while len(sound_queue) > 0:
                source = sound_queue.pop(0)
                audio_length = MP3(source).info.length
                voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=source_name))

                # Supposedly helps with an issue where the sound is sped up
                voice.pause()
                await asyncio.sleep(0.5)
                voice.resume()

                # Wait until the song is finished
                await asyncio.sleep(audio_length + 1)

            # Disconnect from the channel once all the sounds are played
            await voice.disconnect(force=True)


bot.run(DISCORD_TOKEN)
