import json
import os
import random
import shutil

import discord

from bot import bot

price_file = {}
youre_welcomes = {}
users_file = {}


async def init():
    valid_files = await verify_files()

    # Tell main that the files are not valid, and bot needs to be logged out
    if valid_files is not True:
        return valid_files

    with open('../json_files/users.json', 'r') as f:
        user_data = json.load(f)

    with open('../json_files/item_prices.json', 'r') as f:
        price_data = json.load(f)

    with open('../youre_welcome.txt', 'r') as f:
        youre_welcomes_data = f.read().split("\n")

    global users_file
    users_file = user_data

    global price_file
    price_file = price_data

    global youre_welcomes
    youre_welcomes = youre_welcomes_data

    return True


async def reload_files():
    await init()


# USER JSON

@bot.slash_command(name="add_user", description="Add a user to the internal files")
async def add_new_user(ctx, username):
    if len(username) > 0:
        try:
            user = await ctx.guild.fetch_member(username.strip("<@!>"))

        # Intercepts an exception when a user does not provide a snowflake.
        except discord.errors.HTTPException:
            await ctx.respond("Please include the '@' at the start of the name of the user you wish to change",
                              ephemeral=True)

        else:
            if get_user_field(user.id, "file_name") is None:
                add_user(user.id)
                await ctx.respond("User added to system", ephemeral=True)
            else:
                await ctx.respond("User is already in the system", ephemeral=True)


def add_user(member_id):
    if get_user_field(member_id, "file_name") is None:
        users_file[str(member_id)] = {
            "file_name": str(member_id) + ".mp3",
            "points": 1000,
            "bets": 0,
            "play_on_enter": False
        }

        # Dump into file
        with open('../json_files/users.json', 'w') as f:
            json.dump(users_file, f, indent=4)


def update_user(member_id, field, value):
    if users_file is None:
        raise Exception("users_files in json_utils.py is None")

    json_member = users_file[str(member_id)]

    if json_member is not None:
        users_file[str(member_id)][field] = value

        # Dump into file
        with open('../json_files/users.json', 'w') as f:
            json.dump(users_file, f, indent=4)


def get_user_field(member_id, field):
    if users_file is None:
        raise Exception("users_files in json_utils.py is None")

    if str(member_id) in users_file:
        json_member = users_file[str(member_id)]
        return json_member[field]
    return None


def pick_random_user():
    return random.choice(users_file)


# SOUNDS JSON
def get_sound_price(sound_name):
    """
    :param sound_name: name of sound to be played
    :type sound_name: str
    :returns: price to play the sound with the name
    :rtype: int or None
    """

    if price_file is None:
        raise Exception("price_file in json_utils.py is None")

    if sound_name in price_file:
        return price_file[sound_name]["price"]
    return None


def set_sound_price(sound_name):
    if price_file is None:
        raise Exception("price_file in json_utils.py is None")

    return price_file[sound_name]["price"]


async def get_random_youre_welcome():
    if youre_welcomes is None:
        raise FileNotFoundError("price_file in json_utils.py is None")

    return random.choice(youre_welcomes)


def verify_file(file_name):
    if os.path.exists("../json_files/" + file_name + ".json"):
        return True

    # Verify the folder exists
    if not os.path.exists("../json_files/"):
        os.mkdir("../json_files/")

    if os.path.exists("../default/" + file_name + ".json"):
        print("File ../json_files/" + file_name + ".json does not exist. Creating file.")
        shutil.copy("../default/" + file_name + ".json", "../json_files/" + file_name + ".json")
        return True
    else:
        return "Default file " + file_name + " not detected"


async def verify_files():
    # Verify .json files exist
    file_names = ["config", "item_prices", "jackpot", "users"]

    for fn in file_names:
        verify = verify_file(fn)
        if verify is not True:
            return verify

    return True


async def get_user_from_id(user_id):
    name = bot.get_user(user_id)

    if name is None:
        name = await bot.fetch_user(user_id)

    return name
