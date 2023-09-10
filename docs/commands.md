## User Management

### add_user -- `/add_user @username`
Adds a user to the BlockBot system. Must include the `@` for the username. 

This command creates a new entry in the `users.json` with the user's ID.

In most cases, when a user joins a server they will automatically get added to the system.
However, there is some special cases in which a user may not be added (such as the user joining a server before BlockBot).

### nick -- `/nick @username {new_nick}`
### upload -- `/upload {attachment}`
### upload_other -- `/upload {attachment} @username`

---

## Administration

### reload -- `/reload`

---

## Sounds / Intros

### intro -- `/intro`
### play -- `/play {sound_name}`
### shop -- `/shop`

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
### stop -- `/stop`

### command -- `/command {command}`

Runs a server command on a running Minecraft server being hosted through BlockBot

---

## Other

### poll -- `/poll {title} {option1} {option2} | {option3} {option4}`
### roll -- `/roll {number_of_dice} {number_of_faces} | {modifier}`

