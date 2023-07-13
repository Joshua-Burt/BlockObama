import datetime
import time

from colorama import Fore


def timestamp_to_readable(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S -')


async def log(input_str):
    print(Fore.RESET + timestamp_to_readable(time.time()), Fore.RESET + input_str)


async def log_error(input_str):
    print(Fore.RED + timestamp_to_readable(time.time()), input_str + Fore.RESET)
