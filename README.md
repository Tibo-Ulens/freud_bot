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
