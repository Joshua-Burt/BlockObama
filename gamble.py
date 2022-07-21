import asyncio
import random
import json
import json_utils

from discord.ext import tasks

global jackpot_json


async def init():
    with open('json_files/jackpot.json', 'r') as f:
        global jackpot_json
        jackpot_json = json.load(f)


async def gamble(ctx, bot, wager, id_list):
    if not wager.isnumeric() and wager != "all":
        await ctx.send("What")
        return

    author = ctx.message.author
    author_prev_points = int(json_utils.get_user_field(author.id, "points"))

    if wager != "all":
        wager = int(wager)
    else:
        wager = author_prev_points

    if wager <= 0:
        await ctx.send("You can't gamble {} points dumbass".format(wager))
        return

    if author_prev_points < wager:
        await ctx.send("You don't have enough points. You currently have **{}** points".format(author_prev_points))
        return

    value = random.random()
    result = ""
    jackpot_changed = False
    gifted_member = None

    if value <= 0.05:
        json_utils.update_user(author.id, "points", author_prev_points + (wager * 2))
        result = "**{}** has gambled **{}** and tripled their wager.".format(author, wager)

    elif 0.05 < value <= 0.15:
        result = "**{}** has gambled **{}** and broke even.".format(author, wager)

    elif 0.15 < value <= 0.30:
        json_utils.update_user(author.id, "points", author_prev_points + wager)
        result = "**{}** has gambled **{}** and doubled their wager.".format(author, wager)

    elif 0.30 < value <= 0.45:
        multiple = random.random()
        json_utils.update_user(author.id, "points", author_prev_points - wager + round(wager * multiple))
        add_to_jackpot(wager - round(wager * multiple))
        result = "**{}** has gambled **{}** and got {:.2f}x back.".format(author, wager, multiple)
        jackpot_changed = True

    elif 0.45 < value <= 0.6:
        json_utils.update_user(author.id, "points", author_prev_points - round(wager / 2))
        add_to_jackpot(round(wager / 2))
        result = "**{}** has gambled **{}** and lost half of it.".format(author, wager)
        jackpot_changed = True

    elif 0.6 < value <= 0.85:
        multiple = 1 + random.random()
        json_utils.update_user(author.id, "points", author_prev_points - wager + round(wager * multiple))
        result = "**{}** has gambled **{}** and gained {:.2f}x back.".format(author, wager, multiple)

    elif 0.85 < value <= 0.90:
        json_utils.update_user(author.id, "points", author_prev_points - wager)
        add_to_jackpot(round(wager))
        result = "**{}** has gambled **{}** and lost all of it.".format(author, wager)
        jackpot_changed = True

    elif 0.90 < value < 0.99999:
        gifted_member = random.choice(id_list)

        json_utils.update_user(author.id, "points", author_prev_points - wager)
        json_utils.update_user(gifted_member, "points", json_utils.get_user_field(gifted_member, "points") + wager)
        gifted_member_name = await get_user_from_id(bot, gifted_member)

        result = "**{}** has gambled **{}** and has given it to **{}**.".format(author, wager, gifted_member_name)

    elif value >= 0.99999:
        json_utils.update_user(author.id, "points", author_prev_points + get_jackpot_amount())
        result = "**Congrats!** You've won the jackpot of **{}** points!" \
            .format(get_jackpot_amount(), json_utils.get_user_field(author.id, "points"))
        reset_jackpot()
        jackpot_changed = True

    author_curr_points = json_utils.get_user_field(author.id, "points")

    # Output for gifted
    if gifted_member is not None:
        gifted_member_name = await get_user_from_id(bot, gifted_member)
        gifted_member_points = json_utils.get_user_field(gifted_member, "points")

        await ctx.send((result, "**{}'s** current balance is **{}**.\n**{}'s** current balance is **{}**."
                        .format(author, author_curr_points, gifted_member_name, gifted_member_points)))
    # General Output
    else:
        await ctx.send((result, "Their current balance is **{}**".format(author_curr_points)))

    # Ran outta money
    if author_curr_points <= 0:
        await ctx.send("Congratulations, you've lost everything! You've been reset to 100 points")
        json_utils.update_user(author.id, "points", 100)

    # Say jackpot changed
    if jackpot_changed:
        await ctx.send("The jackpot is now **{}**".format(get_jackpot_amount()))


async def get_user_from_id(bot, user_id):
    name = bot.get_user(user_id)

    if name is None:
        name = await bot.fetch_user(user_id)

    return name


async def points(ctx, bot, id_list):
    output = ""
    for i in range(len(id_list)):
        username = await get_user_from_id(bot, id_list[i])
        user_points = json_utils.get_user_field(i, "points")
        user_bets = json_utils.get_user_field(i, "bets")

        output += "> **{}**:\n> \t{} Points \n> \t{} Bets\n".format(username, user_points, user_bets)

    await ctx.send("{}".format(output))


async def pay_points(from_user, to_user, amount):
    json_utils.update_user(from_user, "points", json_utils.get_user_field(from_user, "points") - amount)
    json_utils.update_user(to_user, "points", json_utils.get_user_field(to_user, "points") + amount)


def add_to_jackpot(amount):
    jackpot_json["jackpot"]["points"] += amount

    with open('json_files/jackpot.json', 'w') as f:
        json.dump(jackpot_json, f, indent=4)


def reset_jackpot():
    jackpot_json["jackpot"]["points"] = 0

    with open('json_files/jackpot.json', 'w') as f:
        json.dump(jackpot_json, f, indent=4)


def get_jackpot_amount():
    return jackpot_json["jackpot"]["points"]


@tasks.loop(seconds=5, count=None, reconnect=True)
async def add_points(bot):
    await bot.wait_until_ready()

    channel = bot.get_channel(907101406488559646)
    members = channel.members

    for member in members:
        if not member.bot and member.id != 196360954160742400:
            json_utils.update_user(member.id, "points", json_utils.get_user_field(member.id, "points") + 100)

    afk_channel = bot.get_channel(910698924606652466)
    afk_members = afk_channel.members

    for afk_member in afk_members:
        if not afk_member.bot:
            json_utils.update_user(afk_member.id, "points", json_utils.get_user_field(afk_member.id, "points") - 100)
