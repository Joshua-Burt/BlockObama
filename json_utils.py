import json
import os
import random
import shutil
import sys

global users_file
global price_file
global youre_welcomes


async def init():
    valid_files = await verify_files()

    # Tell main that the files are not valid, and bot needs to be logged out
    if valid_files is not True:
        return valid_files

    with open('json_files/users.json', 'r') as f:
        user_data = json.load(f)

    with open('json_files/item_prices.json', 'r') as f:
        price_data = json.load(f)

    with open('youre_welcome.txt', 'r') as f:
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
def add_user(member_id):
    users_file.append({
        member_id
    })

    users_file[member_id].append({
        "file_name": "None",
        "points": 100,
        "bets": 0,
        "play_on_enter": False
    })


def update_user(member_id, field, value):
    json_member = users_file[str(member_id)]

    if json_member is not None:
        users_file[str(member_id)][field] = value

        # Dump into file
        with open('json_files/users.json', 'w') as f:
            json.dump(users_file, f, indent=4)


def get_user_field(member_id, field):
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

    if sound_name in price_file:
        return price_file[sound_name]["price"]
    return None


def set_sound_price(sound_name):
    return price_file[sound_name]["price"]


# YOU'RE WELCOME JSON
async def get_random_youre_welcome():
    global youre_welcomes
    return random.choice(youre_welcomes)


async def verify_files():
    # Verify .json files exist

    # config.json
    if not os.path.exists("json_files/config.json"):
        if os.path.exists("default/config.json"):
            shutil.copy("default/config.json", "json_files/config.json")
        else:
            return "Default file config.json not detected"

    # item_prices.json
    if not os.path.exists("json_files/item_prices.json"):
        if os.path.exists("default/item_prices.json"):
            shutil.copy("default/item_prices.json", "json_files/item_prices.json")
        else:
            return "Default file item_prices.json not detected"

    # jackpot.json
    if not os.path.exists("json_files/jackpot.json"):
        if os.path.exists("default/jackpot.json"):
            shutil.copy("default/jackpot.json", "json_files/jackpot.json")
        else:
            return "Default file jackpot.json not detected"

    # users.json
    if not os.path.exists("json_files/users.json"):
        if os.path.exists("default/users.json"):
            shutil.copy("default/users.json", "json_files/users.json")
        else:
            return "Default file users.json not detected"

    return True
