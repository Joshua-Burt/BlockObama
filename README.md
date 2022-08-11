# BlockObama
## Overview
The original purpose of creating this bot was to have a small group of friends be able to start and stop a Minecraft server that runs on my computer.

Since then, I've added several features, such as:
- Points system
  - Betting with adjustable odds
  - Spending points on sound clips to play in voice channels
  - Gain points by spending time in voice channel
  - Lose points by spending time in AFK channel
- Rolling dice system
  - Simulates a rolling dice using dice notation
  - e.g. The command ***{prefix}* roll 2d20** will simulate rolling 2 d20 dice

- Voice channel intros
  - Customizable intro sound clips
  - Plays once someone joins a voice channel, recommended to be ~3-6 seconds long

## Use Case
My personal use case is small scale, and I do not believe what I have set up here would scale up to anything more than a single server for friends.

Having the bot control the Minecraft server was the original purpose, and it definitely serves it. Anyone is able to start the server and close it when they are finished, so the server does not need to be running 24/7.

## Setup

The file structure can be found in the docs folder, along with any important info regarding using the bot.

## Notes
This bot is not without fault. The server portion is mostly reliable, however it is possible to cause data-loss/corruption rarely. It is recommended to make regular backups of any World files you have

This project is mainly used for myself, so it can change frequently and without warning. Feel free to contribute regardless.
