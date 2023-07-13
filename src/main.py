import json
import sys
import discord
from colorama import Fore
from discord.ext import commands

# Local Files
import json_utils
import server
import gamble
import sounds
import intro
import roll
from log import log, log_error
from bot import bot

# Load config file to obtain the token
config_integrity = json_utils.verify_file("config")
if config_integrity is not True:
    print(config_integrity)
    sys.exit()

with open('../json_files/config.json', 'r') as f:
    config = json.load(f)

# Constants
DISCORD_TOKEN = config["token"]

if DISCORD_TOKEN == "":
    print(Fore.RED + "Default token given. Please change token in config.json")
    sys.exit()


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    await log(f'Logged in as {bot.user}' + Fore.YELLOW + '\nPowered on [o.o]' + Fore.RESET)
    print("---------------------------------")

    # Verify that the required .json files exist
    json_msg = await json_utils.init()
    if json_msg is not True:
        await log_error(json_msg)
        await bot.close()

    await intro.init(config["max_intro_length"])
    await gamble.init(config["gamble_channel"])
    await server.init(config["server_path"])
    await sounds.init()

    game = discord.Game(config["default_activity"])
    await bot.change_presence(status=discord.Status.online, activity=game)

    await start_points_loop()


@bot.event
async def on_member_join(member: discord.Member):
    if member.bot:
        return

    await log(f"Adding member {Fore.YELLOW + member.name + Fore.RESET}")
    await json_utils.add_user(member.id)


@bot.slash_command(name="say", description="Repeat the inputted message")
async def say(ctx, message):
    await ctx.send(message)
    await ctx.respond("Said the words", ephemeral=True)


@bot.message_command(name="mock_message", description="Mock the selected message")
async def mock_message(ctx, message: discord.Message):
    if message.author == bot.user:
        await ctx.respond('no')
    else:
        message_text = message.content

        if len(message_text) > 0:
            await ctx.respond(await mockify(message_text))
        else:
            await ctx.respond("There wasn't any text to mock", ephemeral=True)


@bot.slash_command(name="mock", description="Mock the last message sent")
async def mock(ctx):
    logs = await ctx.channel.history(limit=1).flatten()

    if logs[0].author == bot.user:
        await ctx.respond('no')
    else:
        message_text = logs[0].content

        if len(message_text) > 0:
            await ctx.respond(await mockify(message_text))
        else:
            await ctx.respond("There wasn't any text to mock", ephemeral=True)


@bot.slash_command(name="pay", description="Pay amount of points to another user")
async def pay(ctx, payee, amount):
    if len(payee) > 0 and len(amount) > 0 and int(amount) > 0:
        if await json_utils.get_user_field(ctx.author.id, "points") > int(amount):
            await gamble.pay_points(ctx.author.id, payee.strip("<@!>"), int(amount))

            await ctx.respond("**{}** paid **{}** - **{:,}** points".format(
                await json_utils.get_user_from_id(ctx.author.id),
                await json_utils.get_user_from_id(payee.strip("<@!>")), int(amount)))


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
            await ctx.respond("Please include the '@' at the start of the name of the user you wish to change",
                              ephemeral=True)

        else:
            await user.edit(nick=new_nick)
            await ctx.respond(f"Changed {user.name}'s nickname to {new_nick}", ephemeral=True)


@bot.slash_command(name="reload", description="Reloads the bot's internal files")
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
    # Don't respond to bot messages, that spells disaster
    if message.author.bot:
        return

    saying = await json_utils.get_saying_from_trigger(message)
    if saying:
        response = await json_utils.get_random_response(saying)

        # Prevent a blank message from being sent
        if len(response) > 0:
            await message.channel.send(response)
        else:
            await log_error("on_message - Responses must be longer than 0 characters")


# Helper functions

async def start_points_loop():
    guilds = bot.guilds
    voice_channels = []
    afk_channels = []

    # Find all voice channels that the bot connects to, then add that to the respective list
    for g in range(len(guilds)):
        # Get all non-afk channels
        for c in range(len(guilds[g].voice_channels)):
            voice_channels.append(guilds[g].voice_channels[c].id)

        # Add the afk channel, if it exists
        if guilds[g].afk_channel:
            afk_channels.append(guilds[g].afk_channel.id)

    if not gamble.points_loop.is_running():
        gamble.points_loop.start(voice_channels, afk_channels)


# Transforms a string into a mocked string
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


class Error(Exception):
    def __init__(self, message):
        super().__init__(Fore.RED + message)


bot.run(DISCORD_TOKEN)
