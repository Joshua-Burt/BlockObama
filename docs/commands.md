# Commands

## User Management

### add_user -- `/add_user @username`
Adds a user to the BlockBot system.

This command creates a new entry in the `users.json` with the user's ID.

In most cases, when a user joins a server they will automatically get added to the system.
However, there is some special cases in which a user may not be added (such as the user joining a server before BlockBot).

### nick -- `/nick @username {new_nick}`
Changes the displayed nickname of the selected user. BlockBot is able to change the username of any user with a lower role.

This command does not work for server owners, as they will always have the highest role and cannot have other users change their username.

### upload -- `/upload {attachment}`
Uploads a new .mp3 (or replaces an existing one) to be used as the voice channel intro of the user executing the command.

### upload_other -- `/upload {attachment} @username`
Uploads a new .mp3 (or replaces an existing one) to be used as the voice channel intro of the provided user.

This is recommended to be limited to Admin roles.

---

## Administration

### reload -- `/reload`
Reloads the JSON files by loading them into the working memory.

Useful when manually editing JSON files on a running bot. Whether doing that is recommended is up to opinion.

---

## Sounds / Intros

### intro -- `/intro`
Toggles if your intro plays when you join a voice channel

### play -- `/play {sound_name}`
Plays the sound with the given name.

Each sound has a price, and it won't play the sound if the user doesn't have enough points.
<br>If the user has enough points, it gets subtracted from their current balance.

### shop -- `/shop`
Displays all the sounds and their prices currently in the `item_prices.json`.

---

## Points System

### gamble -- `/gamble {wager}`
Gambles the amount of points given in `wager`.
Gambling gives the user a chance to increase, decrease, or keep their points balance.

There are many ways for the gamble to go, such as:
<br>winning 2x, 3x the wager; losing half or all the wager; giving the wager to another user; etc.

> Note: In `config.json`, there is a "gambling_channel" field which needs to contain the channel ID of the 
> channel which allows gambling. This is because this command can very quickly spam a channel, so it is
> recommended to have a dedicated channel.

### pay -- `/pay @payee {amount}`
Sends a given amount of points to `@payee`.

Simply subtracts the amount from the payer's balance and adds it to the payee's balance.

### points -- `/points`
Sends a message showing the leaderboard of points. This is ordered from the greatest points to least.

This also shows the total number of bets each user has made.

---

## Text Based Commands

### mock -- `/mock`
Mocks the last sent message. BlockBot will not mock its own messages, it knows better.

e.g. if the last message sent is `Hello, World!`, using /mock will have BlockBot reply with `HeLlO, WoRlD!`.

> There is also a Message Command (right-click on a message > Apps > mock_message) that does this same function
> but on any selected message

### pyramid -- `/pyramid {word}`
Creates a word pyramid of the given word.

e.g. If the given word is "Hello", BlockBot will respond with:

```
H
He
Hel
Hell
Hello
Hell
Hel
He
H
```


### say -- `/say {message}`
Simply responds with the given message, to appear as BlockBot said it.

It sends the message to the channel the command was executed in, and a defer command response is sent.
This makes it so `{username} used /say` does not appear above the message.

---

## Minecraft Server

### start -- `/start`
Starts the Minecraft server described in `config.json`

### stop -- `/stop`
Stops the Minecraft server described in `config.json`

### command -- `/command {command}`
Runs a server command on a running Minecraft server being hosted through BlockBot

---

## Other

### poll -- `/poll {title} {option1} {option2} | {option3} {option4}`
Creates a poll for users to vote on. It sends a message with the title, all given options, and an appropriate amount of buttons for users to click.

Each user can only vote once, and currently votes cannot be recast.

Two options are required, but option3 and option4 are optional. 

> Currently, polls essentially last forever (or until BlockBot is stopped/restarted). This is likely to change in the future
> as BlockBot needs to keep track in memory of every user voted for every poll.

### roll -- `/roll {number_of_dice} {number_of_faces} | {modifier}`
Rolls one or more die with the given faces, and with an optional modifier.

This does not need to abide by standard dice faces (4, 6, 8, 10, etc.) and can be any given integer.

The command converts the roll into dice notation (e.g. 2d20 + 3) which gets interpreted in `roll.py`

> Note: This last part should probably not happen, as it simply combines the variables just to separate them again
