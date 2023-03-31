# BlockBot
## Overview

- Voice channel intros
  - Customizable intro sound clips
  - Plays once someone joins a voice channel
  
- Controlling a Minecraft server
  - Users can start and stop a server hosted on the same machine
  
- Points system
  - Betting with adjustable odds
  - Spending points on sound clips to play in voice channels
  - Gain points by spending time in voice channel
  - Lose points by spending time in AFK channel
  
- Rolling dice system
  - Simulates a rolling dice using dice notation
  - e.g. The command **/roll 2d20** will simulate rolling 2 d20 dice


- Anyone can change nicknames (if the bot is a higher role than target)

## Use Case

Having the bot control the Minecraft server was the original purpose, and it definitely serves it. Anyone is able to start the server and close it when they are finished, so the server does not need to be running 24/7.

The intros are a great success in my experience, as it as a personal touch to every user

## Setup

The file structure can be found in the docs folder, along with any important info regarding using the bot.

Recommended to use [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701) on Windows (or equivalent on other operating systems) to take full advantage of the log colouring.

## Notes
This bot is not without fault. The server portion is mostly reliable, however it is possible to cause data-loss/corruption to the server rarely. It is recommended to make regular backups of any World files you have

This project is mainly used for myself, so it can change frequently and without warning. Feel free to contribute regardless.
