# First-time Running

The first time the BlockBot is run, it will generate several files, each of which is described below.

`config.json`, `item_prices.json`, `jackpot.json`, `sayings.json`, and `users.json`

# File Descriptions
## config.json

This file contains the basic information for the bot to function. 

The most important is the `token`. 
<br>This is the token your bot will use to log into Discord's services, and must be obtained through the [Discord Developer Portal](https://discord.com/developers/applications). The bot will not run without this token.

| Identifier           | Type   | Description                                                                                  |
|----------------------|--------|----------------------------------------------------------------------------------------------|
| token                | int    | the Discord bot's token                                                                      |
| server_path          | string | the path to a Minecraft server with a start.bat in it                                        |
| gamble_channel       | int    | channel id of a text channel that users can use the bet command                              |
| max_intro_length     | int    | the maximum length (in seconds) a user uploaded intro can be. Prevents absurdly long intros. |
| default_activity     | string | the text displayed under the bot's name (e.g. "Playing Not Minecraft")                       |

```json
{
    "token": "Nzk3NjUxxDUMMYDATAxxNOTAREALKEYxxfdT4hT",
    "server_path": "C:\\Path\\To\\Server",
    "gamble_channel": -1,
    "max_intro_length": 8,
    "default_activity": "Not Minecraft"
}
```

---

## item_prices.json:

This contains the list of sounds that can be purchased using `/play {sound_name}`.

The sound files are stored under `/sounds/shop_sounds/{sound_name}.mp3`

> Note: BlockBot currently only plays *.mp3 files

Each sound has a name and a price. When a member plays a sound, the price is subtracted from the member's point balance.
If the member cannot afford the price, the sound is not played.

The JSON key is the name of the file (without the .mp3 extension).
 
> Currently, the *.mp3 file must be manually placed in the sounds folder, and the item_prices.json file 
> must be manually edited. This will be made automatic with a command at a later date.

### Example:

```json
{
  "anime_wow": {
    "price": 2000
  },
  "knocking": {
    "price": 12000
  },
  "oh_my": {
    "price": 1000
  }
}
```

---

## jackpot.json:

The purpose of this file is to keep track of the jackpot of the betting feature. 
Everytime a member loses points while betting, the amount they lost gets added to the jackpot.

There is a small chance everytime  a member bets that they win the entire contents of the jackpot.

This is the simplest json file, and only contains 1 field.

| Identifier | Type   | Description                               |
|------------|--------|-------------------------------------------|
| points     | int    | the total number of points in the jackpot |


### Example:

```json
{
    "jackpot": {
        "points": 510423
    }
}
```

---

## sayings.json:

This file contains lists of words/sentences BlockBot will listen for, and responses to those words/sentences.

When a message is sent to a channel with BlockBot, it will look at the list of trigger words, 
and sends a random response from the response list for that trigger.

This listening and responding is done within `on_message()` in `main.py`

There can be multiple triggers and multiple responses for every entry.

### Example:
```json
{
  "0":{
    "trigger": ["thanks obama", "thank you obama", "thx obama", "tanks obama", "ty obama", "thank u obama"],
    "response": ["You're welcome","Not a problem","No trouble","No worries","My pleasure","Happy to help","Not at all"]
  },
  "1": {
    "trigger": ["crazy", "rats make me crazy", "i was crazy once", "a rubber room with rats","they locked me in a room, a rubber room","they locked me in a room a rubber room"],
    "response": ["Crazy? I was crazy once", "They locked me in a room", "They locked me in a room, a rubber room", "Crazy? I was crazy once. They locked me in a room, a rubber room. A rubber room with rats.", "Rats make me crazy", "Crazy?"]
  }
}
```

---

## users.json:

This file keeps track of each member that has been added to the BlockBot system.

| Identifier    | Type   | Description                                                          |
|---------------|--------|----------------------------------------------------------------------|
| JSON key      | int    | the id of the Discord member                                         |
| file_name     | string | the file name for that member's intro sound (Typically {id}.mp3)     |
| points        | int    | tracker for number of points the member currently has                |
| bets          | int    | tracker for how many bets the member has made                        |
| play_on_enter | bool   | whether the member's intro will play when they enter a voice channel |

> Note: BlockBot currently only plays *.mp3 files. The file_name field must contain .mp3 at the end

### Example:

```json
{
    "89012576xxDUMMYDATAxx234083201": {
        "file_name": "89012576xxDUMMYDATAxx234083201.mp3",
        "points": 4123,
        "bets": 223,
        "play_on_enter": true
    },

    "4213942346xxDUMMYDATAxx4912033": {
        "file_name": "4213942346xxDUMMYDATAxx4912033.mp3",
        "points": 500,
        "bets": 10,
        "play_on_enter": false
    }
}
```


