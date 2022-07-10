import asyncio
import random


async def gamble(ctx, bot, wager, json_file, update_json, id_list):
    if not wager.isnumeric() and wager != "all":
        await ctx.send("What")
        return

    author = ctx.message.author
    member = json_file[str(author.id)]

    if wager != "all":
        wager = int(wager)
    else:
        wager = int(member["points"])

    if wager <= 0:
        await ctx.send("You can't gamble {} points dumbass".format(wager))
        return

    if member["points"] < wager:
        await ctx.send("You don't have enough points. You currently have **{}** points".format(member["points"]))
        return

    value = random.random()

    if value <= 0.05:
        update_json(author.id, "points", member["points"] + (wager * 2))
        await ctx.send(
            "**{}** has gambled **{}** and tripled their wager. Their current balance is **{}**".format(author, wager,
                                                                                            member["points"]))

    elif 0.05 < value <= 0.15:
        await ctx.send(
            "**{}** has gambled **{}** and broke even. Their current balance is **{}**".format(author, wager, member["points"]))

    elif 0.15 < value <= 0.30:
        update_json(author.id, "points", member["points"] + wager)
        await ctx.send("**{}** has gambled **{}** and doubled their wager. Their current balance is **{}**".format(author, wager,
                                                                                                       member[
                                                                                                           "points"]))
    elif 0.30 < value <= 0.5:
        multiple = random.random()
        update_json(author.id, "points", member["points"] - wager + round(wager * multiple))
        await ctx.send(
            "**{}** has gambled **{}** and got {:.2f}x back. Their current balance is **{}**".format(author, wager, multiple,
                                                                                         member["points"]))

    elif 0.50 < value <= 0.65:
        update_json(author.id, "points", member["points"] - round(wager / 2))
        await ctx.send(
            "**{}** has gambled **{}** and lost half of it. Their current balance is **{}**".format(author, wager,
                                                                                        member["points"]))

    elif 0.65 < value <= 0.80:
        multiple = 1 + random.random()
        update_json(author.id, "points", member["points"] - wager + round(wager * multiple))
        await ctx.send(
            "**{}** has gambled **{}** and gained {:.2f}x back. Their current balance is **{}**".format(author, wager, multiple,
                                                                                            member["points"]))

    elif 0.80 < value <= 0.90:
        update_json(author.id, "points", member["points"] - wager)
        await ctx.send(
            "**{}** has gambled **{}** and lost all of it. Their current balance is **{}**".format(author, wager, member["points"]))

    elif 0.90 < value <= 1:
        gifted_member = random.choice(id_list)

        update_json(author.id, "points", member["points"] - wager)
        update_json(gifted_member, "points", json_file[str(gifted_member)]["points"] + wager)
        gifted_member_name = await get_user_from_id(bot, gifted_member)

        await ctx.send("**{}** has gambled **{}** and has given it to **{}**. Their current balance is **{}** "
                       "and **{}** has **{}** points"
                       .format(author, wager, gifted_member_name, member["points"], gifted_member_name,
                               json_file[str(gifted_member)]["points"]))

    if json_file[str(author.id)]["points"] <= 0:
        await ctx.send("Congratulations, you've lost everything! You've been reset to 100 points")
        update_json(author.id, "points", 100)


async def get_user_from_id(bot, user_id):
    name = bot.get_user(user_id)

    if name is None:
        name = await bot.fetch_user(user_id)

    return name


async def points(ctx, bot, json_file, id_list):
    output = ""
    for i in range(len(id_list)):
        username = await get_user_from_id(bot, id_list[i])
        output += "> **{}**:\n> \t{} Points \n> \t{} Bets\n".format(username, json_file[str(id_list[i])]["points"], json_file[str(id_list[i])]["bets"])

    await ctx.send("{}".format(output))


async def add_points(bot, update_json, json_file):
    await bot.wait_until_ready()

    while not bot.is_closed():
        await asyncio.sleep(300)

        channel = bot.get_channel(907101406488559646)
        members = channel.members

        for member in members:
            if not member.bot and member.id != 196360954160742400:
                update_json(member.id, "points", json_file[str(member.id)]["points"] + 100)

        afk_channel = bot.get_channel(910698924606652466)
        afk_members = afk_channel.members

        for afk_member in afk_members:
            if not afk_member.bot:

                update_json(afk_member.id, "points", json_file[str(afk_member.id)]["points"] - 100)
