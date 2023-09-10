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
### pay -- `/pay @payee {amount}`
### points -- `/points`

---

## Text Based Commands

### mock -- `/mock`
### pyramid -- `/pyramid {word}`
### say -- `/say {message}`

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
### roll -- `/roll {number_of_dice} {number_of_faces} | {modifier}`

