# Discord-rawrbot

my discord bot for Salem's server

If you wish to join the server, please use this [link](https://discord.gg/phHzxjNWbq)

If you wish to add the bot, do so [here](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot)

The only dependency you need is discord.py (I think).

Let's start a changelog ig?
#### 1.idk,1?
- removed a giant comment of unused code (not sure if this was pushed, but I removed it from my own)
- Used a JSON file to store stuff instead, so that it's easier for other people
- added a new function to grab stuffs from the thing. Probably a better way to do it tbh
- added emojis to counting
- if you store the token in base64, then it auto undoes it. You don't need to change it to base64 if you already have it not in that. (I'm just too lazy to change it back for my own token)

#### 1.2
- Added multiple commands
- Server commands:
    - mute <voice_channel> <user> [mute: bool = True] [time: int = 5]
        - Mutes a user. Set time = 0 to permanently mute them. Set mute = False to unmute
    - deafen <voice_channel> <user> [deafen: bool = True] [time: int = 5]
        - Same as above, deafens instead.
    - move_single <user> <voice_channel>
        - Moves one user into another voice channel. Does nothing if the channel is the same as the current channel or if the user is not in a voice channel.
    - move_all <voice_channel> <new_channel> [lock_channel: bool = False]
        - Moves all users from voice_channel to new_channel. If lock_channel is true, it will lock the channel to prevent users from joining the channel again until manually undone
- User commands
    - translate <text> <from_language> <to_language>
        - Translates text from one language to another. You can use a different language than what is listed by using the ISO standard name or with RFC 3066
    - upload <link>
        - downloads a video from a site, and uploads it onto sxcu.net and shares the link as an embed.