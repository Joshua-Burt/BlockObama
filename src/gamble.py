import random
import json
from discord.ext import tasks

from json_utils import get_user_from_id, get_user_field, update_user
from bot import bot

global jackpot_json
global id_list
gambling_channel_id = -1


async def init(gamble_channel):
    global gambling_channel_id
    gambling_channel_id = gamble_channel

    with open('../json_files/jackpot.json', 'r') as f:
        global jackpot_json
        jackpot_json = json.load(f)

    with open('../json_files/users.json', 'r') as f:
        global id_list
        id_list = list(json.load(f).keys())


@bot.slash_command(name="gamble")
async def bet(ctx, wager):
    if ctx.channel.id == gambling_channel_id:
        await gamble(ctx, wager)

        author_id = ctx.author.id
        update_user(author_id, "bets", get_user_field(author_id, "bets") + 1)
    else:
        await ctx.respond("This isn't the gambling channel dummy")


async def gamble(ctx, wager):
    if not wager.isnumeric() and wager != "all":
        await ctx.respond("What")
        return

    author = ctx.author
    author_prev_points = int(get_user_field(author.id, "points"))

    # If the wager is an integer value, simply cast it to an integer
    # If it is "all", get the total amount of points the user has
    if wager != "all":
        wager = int(wager)
    else:
        wager = author_prev_points

    if wager <= 0:
        await ctx.respond(f"You can't gamble {wager} points dumbass")
        return

    if author_prev_points < wager:
        await ctx.respond(f"You don't have enough points. You currently have **{author_prev_points:,}** points")
        return

    value = random.random()
    result = ""
    jackpot_changed = False
    gifted_member_id = None

    # Triple the wager
    if value <= 0.05:
        await add_points(author.id, wager * 2)
        result = f"**{author}** has gambled **{wager:,}** and tripled their wager."

    # Break even
    elif 0.05 < value <= 0.15:
        result = f"**{author}** has gambled **{wager:,}** and broke even."

    # Doubled the wager
    elif 0.15 < value <= 0.30:
        await add_points(author.id, wager)
        result = f"**{author}** has gambled **{wager:,}** and doubled their wager."

    # Lose some percentage of the wager
    elif 0.30 < value <= 0.45:
        multiple = random.random()
        amount = wager - round(wager * multiple)

        await add_points(author.id, -amount)
        await add_to_jackpot(amount)

        result = f"**{author}** has gambled **{wager:,}** and got {multiple:.2f}x back."
        jackpot_changed = True

    # Lose half of the wager
    elif 0.45 < value <= 0.6:
        amount = round(wager / 2)

        await add_points(author.id, -amount)
        await add_to_jackpot(amount)

        result = f"**{author}** has gambled **{wager:,}** and lost half of it."
        jackpot_changed = True

    # Gain some percentage of the wager
    elif 0.6 < value <= 0.85:
        multiple = 1 + random.random()
        amount = round((wager * multiple) - wager)

        await add_points(author.id, amount)
        result = f"**{author}** has gambled **{wager:,}** and gained {multiple:.2f}x back."

    # Lose the entire wager
    elif 0.85 < value <= 0.90:
        await add_points(author.id, -wager)
        await add_to_jackpot(wager)

        result = f"**{author}** has gambled **{wager:,}** and lost all of it."
        jackpot_changed = True

    # Give the wager to a random user
    elif 0.90 < value < 0.999:
        gifted_member_id = random.choice(id_list)

        await add_points(author.id, -wager)
        await add_points(gifted_member_id, wager)

        gifted_member_name = await get_user_from_id(gifted_member_id)

        result = f"**{author}** has gambled **{wager:,}** and has given it to **{gifted_member_name}**."

    # Won the jackpot!
    else:
        await add_points(author.id, await get_jackpot_amount())
        result = f"**Congrats!** You've won the jackpot of **{await get_jackpot_amount():,}** points!"

        await reset_jackpot()
        jackpot_changed = True

    author_curr_points = get_user_field(author.id, "points")

    # Output for gifted
    if gifted_member_id is not None:
        gifted_member_name = await get_user_from_id(gifted_member_id)
        gifted_member_points = get_user_field(gifted_member_id, "points")

        await ctx.respond(' '.join((result,
                                    f"\n**{author}'s** current balance is **{author_curr_points:,}**."
                                    f"\n**{gifted_member_name}'s** current balance is **{gifted_member_points:,}**.")))
    # General Output
    else:
        await ctx.respond(' '.join((result, f"Their current balance is **{author_curr_points:,}**")))

    # Ran outta money
    if author_curr_points <= 0:
        await ctx.send("Congratulations, you've lost everything! You've been reset to 1000 points")
        update_user(author.id, "points", 1000)

    # Say jackpot changed
    if jackpot_changed:
        await ctx.send(f"The jackpot is now **{await get_jackpot_amount():,}**")


async def add_points(user_id, amount):
    author_prev_points = int(get_user_field(user_id, "points"))
    update_user(user_id, "points", author_prev_points + amount)


@bot.slash_command(name="points", description="Display the points of each member")
async def points(ctx):
    output = ""
    for i in range(len(id_list)):
        username = await get_user_from_id(id_list[i])
        user_points = get_user_field(id_list[i], "points")
        user_bets = get_user_field(id_list[i], "bets")

        output += f"> **{username}**:\n> \t{user_points:,} Points \n> \t{user_bets:,} Bets\n"

    await ctx.respond("{}".format(output))


async def pay_points(from_user, to_user, amount):
    update_user(from_user, "points", get_user_field(from_user, "points") - amount)
    update_user(to_user, "points", get_user_field(to_user, "points") + amount)


async def add_to_jackpot(amount):
    jackpot_json["jackpot"]["points"] += amount

    with open('../json_files/jackpot.json', 'w') as file:
        json.dump(jackpot_json, file, indent=4)


async def reset_jackpot():
    jackpot_json["jackpot"]["points"] = 0

    with open('../json_files/jackpot.json', 'w') as file:
        json.dump(jackpot_json, file, indent=4)


async def get_jackpot_amount():
    return jackpot_json["jackpot"]["points"]


@tasks.loop(minutes=3, count=None, reconnect=True)
async def points_loop(voice_channel_ids, afk_channel_ids):
    await bot.wait_until_ready()

    if len(voice_channel_ids) > 0:
        for channel_id in voice_channel_ids:
            channel = bot.get_channel(channel_id)
            members = channel.members

            for member in members:
                if not member.bot and str(member.id) in id_list:
                    update_user(member.id, "points", get_user_field(member.id, "points") + 100)

    if len(afk_channel_ids) > 0:
        for channel_id in afk_channel_ids:
            afk_channel = bot.get_channel(channel_id)
            afk_members = afk_channel.members

            for afk_member in afk_members:
                if not afk_member.bot and str(afk_member.id) in id_list:
                    update_user(afk_member.id, "points", get_user_field(afk_member.id, "points") - 100)
