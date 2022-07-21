import json
import random

global users_file
global price_file
global youre_welcomes


def init():
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
    json_member = users_file[str(member_id)]

    if json_member is not None:
        return json_member[field]
    return None


# SOUNDS JSON
def get_sound_price(sound_name):
    return price_file[sound_name]["price"]


def set_sound_price(sound_name):
    return price_file[sound_name]["price"]


# YOU'RE WELCOME JSON
async def get_random_youre_welcome():
    global youre_welcomes
    return random.choice(youre_welcomes)