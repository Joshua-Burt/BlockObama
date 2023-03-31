__author__ = "Joshua Burt"

import asyncio
import datetime
import time
import json
from os.path import exists
from pathlib import Path

import discord

from colorama import Fore
from discord import option
from discord.ext import commands

# Local Files
from mutagen.mp3 import MP3

import json_utils
import roll as rl
import server as mcserver
import gamble
import sounds

with open('json_files/config.json', 'r') as f:
    config = json.load(f)

# Constants
DISCORD_TOKEN = config["token"]
bot = discord.Bot(intents=discord.Intents.all())

points_loop = None
sound_queue = []


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    await log('Logged in as {0.user}'.format(bot) + Fore.YELLOW + '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    game = discord.Game("your mom")
    await bot.change_presence(status=discord.Status.online, activity=game)

    await json_utils.init()
    await gamble.init()
    await sounds.init(play_sound)

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

    game = discord.Game("Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.slash_command(name="stop", description="Stop the Minecraft Server")
async def stop_server(ctx):
    await log("Stopped the server")
    await mcserver.stop(ctx)

    game = discord.Game("your mom")
    await bot.change_presence(status=discord.Status.online, activity=game)

@option(
    "intro_mp3",
    description="How much to add/subtract from the total roll",
    required=False,
    default=0
)
@bot.slash_command(name="intro", description="Toggle your intro when joining a voice call, or change your intro")
async def intro(ctx):
    if ctx.message.attachments:
        print(ctx.message.attachments)
        return

    new_play_on_enter = not json_utils.get_user_field(ctx.author.id, "play_on_enter")
    json_utils.update_user(ctx.author.id, "play_on_enter", new_play_on_enter)

    await ctx.respond(("Your intro is now ON" if new_play_on_enter else "Your intro is now OFF"), ephemeral=True)


@bot.slash_command(name="upload")
@option(
    "attachment",
    discord.Attachment,
    description="An .mp3 file to be used as your intro. Max {} seconds.".format(config["max_intro_length"]),
    required=True,
)
async def upload_intro(ctx: discord.ApplicationContext, attachment: discord.Attachment):
    if attachment.content_type == "audio/mpeg":
        file = await attachment.to_file()

        # Verify the length is less than the max
        if MP3(file.fp).info.length > config["max_intro_length"]:
            await ctx.respond("Intros must be less than", config["max_intro_length"])
            return

        # Apply the new file
        file_name = json_utils.get_user_field(ctx.author.id, "file_name")

        await attachment.save(Path(str(Path.cwd()) + "/downloads/intros/{}".format(file_name)))
        await ctx.respond("Your intro has been changed")
    else:
        await ctx.respond("Please upload an .mp3 file")
    #
    # var = attachment.content_type
    # await attachment.save(Path("/downloads/intros/" + ))



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
@option(
    "sound_name",
    description="Name of the sound from the shop",
    required=False,
    default=""
)
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
        if len(new_nick) > 32:
            await ctx.respond("Nicknames cannot be longer than 32 characters", ephemeral=True)
            return

        try:
            user = await ctx.guild.fetch_member(username.strip("<@!>"))

        # Intercepts an exception when a user does not provide a snowflake.
        except discord.errors.HTTPException:
            await ctx.respond("Please include the '@' at the start of the name of the user you wish to change", ephemeral=True)

        else:
            await user.edit(nick=new_nick)
            await ctx.respond("Changed {}'s nickname to {}".format(user.name, new_nick), ephemeral=True)


@bot.slash_command(name="wan", description="Hello there")
async def wan(ctx):
    await ctx.respond("Hello there")
    await play_sound(ctx.author, "downloads/hello_there.mp3")


@bot.slash_command(name="reload", description="Reloads the bot's internal files")
@commands.is_owner()
async def reload(ctx):
    await log("Reloading JSON files...")

    await json_utils.reload_files()

    await ctx.respond("Reloaded.", ephemeral=True)
    await log("Files reloaded")


@bot.event
async def on_command_error(ctx, error: discord.ext.commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        # TODO: Inform user that the command doesn't exist
        return
    raise error


@bot.event
async def on_message(message):
    thank_you_messages = ['thanks obama', 'thank you obama', 'thx obama', 'tanks obama', 'ty obama', 'thank u obama']
    if message.content.lower() in thank_you_messages:
        await message.channel.send(await json_utils.get_random_youre_welcome())


async def play_sound(member: discord.Member, source_name):

    if exists(source_name):

        channel = member.voice.channel
        sound_queue.append(source_name)

        if channel and bot.user not in channel.members:
            voice = await channel.connect()

            while len(sound_queue) > 0:
                source = sound_queue.pop(0)
                audio_length = MP3(source).info.length
                voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=source))

                voice.pause()
                await asyncio.sleep(0.5)
                voice.resume()

                await asyncio.sleep(audio_length + 2)

            await voice.disconnect(force=True)


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


class Error (Exception):
    def __init__ (self, message):
        super().__init__(Fore.RED + message)


bot.run(DISCORD_TOKEN)
