# FreudBot

UGent Discord verification and shenanigans bot

## Contributing

See [the contributing guide](CONTRIBUTING.md) for instructions on how to contribute to this project.

## Features

Unless stated otherwise all commands are slash commands

### Hooks

 - bot mentioned: Responds to the message with a random Freud quote

 - new member joins: Sends the member a DM with verification instructions or verifies them
 automatically if they are already verified in another Freud-enabled server

 - 📌 emoji reaction: If enough people react to a message with this emoji it will be pinned
 automatically.
 The amount of reactions needed for this is configurable on the website.

### Commands

#### Configuration

***The configuration commands are largely deprecated and have been replaced by the config website
https://freudbot.org***

 - `$freud_sync` \
 (MESSAGE COMMAND) \
 (MANAGE GUILD) \
 force-syncs the bot's slash commands to
 whatever guild it's connected to. This can be used after a new version of the bot goes live to
 ensure all commands are up to date, however just waiting for around an hour will achieve the same
 goal.

 - `/config admin_role` \
 (MANAGE GUILD) \
 Set the role that 'admin' members will have, this is used to check permissions for the other
 `/config` commands

 - `/config verified_role` \
 (ADMIN) \
 Set the role that's given to verified members

 - `/config logging_channel` \
 (ADMIN) \
 Set the channel into which log messages will be
 posted

 - `/config confession_channel` \
 (ADMIN) \
 Set the channel where approved confessions will be posted

 - `/config confession_approval_channel` \
 (ADMIN) \
 Set the channel where confessions awaiting approval will be posted (this should be a channel only
 admins can access)

#### Verification

 - `/verify` - Sends a DM to the user with verification instructions, this can be used in case the
 user didn't receive a DM or if the previous messsages buttons have expired.

#### Confessions

Confessions can be sent as replies to other confessions by adding the confession ID as an optional
argument.

eg.
You can reply to "Anonymous Confession (#14) - I like ducks"
with `/confess normal "So do I" "14"`

Note: this is a bit scuffed at the moment and might not work exceptionally well, bugfixes pending.

 - `/confess normal <confession> [<reply>]` - Sends a normal, anonymous confession.

 - `/confess russian <confession> [<reply>]` - Sends a russian roulette confession with a 1/6
 chance of exposing the user who sent it

 - `/confess extreme <confession> [<reply>]` - Sends an extreme roulette confession with a 1/2
 chance of exposing the user who sent it

#### Message Scheduling

Working with time in python is pain, so this command is also pain.
Use at your own risk.

 - `/schedule <channel> <time> [<timezone>] [<message>]` - Schedules a message to be sent in
 `<channel>` at a given `<time>` \
   - `<time>` is a string in the format "%Y/%m/%d %H:%M"
   - `<timezone>` is the timezone of your timestamp (default UTC)
   (UTC = 0000, CET = 0100, CEST = 0200)
   - `<message>` can be given inline or left empty, if left empty a popup will appear with more
   space to type your message.

#### FreudPoints

FreudPoints aren't exceptionally useful at this point, but hopefully they will eventually have
some purpose like a shop mechanic.

 - `/freudpoint award <user> [<amount>]` - Awards `<user>` `<amount>` (default 1) FreudPoint(s)

#### Freudr

Freudr Dating Service, because discord users are too afraid of actual social interaction.
When 2 users match, FreudBot will send them both a DM to congratulate them on their newfound
love.

 - `/freudr like <user>` - Adds a user to your likes (you can only like the same user once every
 24 hours)

 - `/freudr unlike <user>` - Removes a user from your likes

 - `/freudr list` - See a list of your likes and matches

#### Statistics

At the moment FreudBot doesn't keep track of a whole lot of statistics, but this should change in
the "near" future.

 - `/freudstat me` - See an overview of the statistics FreudBot tracks about you

 - `/freudstat profile <user>` - See an overview of the statistics FreudBot tracks about another
 user

 - `/freudstat leaderboard` - See the leaderboards for the stats FreudBot tracks, selectable with a
 dropdown menu

#### Random

- `/mommy` - You can figure this one out for yourself

#### Link Shortcuts (DEPRECATED)

 - `/drive <shortcut>` - Send a link to a hardcoded google drive folder
 At the moment this is only useful for the psychology discord, so other servers should disable this
 command

## Running

The latest release of the bot can be ran using `make`, this will pull the
latest version from https://ghcr.io.

The bot can also be built localy using `make dev`, this will use the provided
[dockerfile](Dockerfile) to build and run a local image.
