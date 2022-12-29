# FreudBot

UGent Psychology Discord server bot

## Contributing

See [the contributing guide](CONTRIBUTING.md) for instructions on how to contribute to this project.

## Features

Unless stated otherwise all commands are slash commands

### Commands

#### Configuration

 - `$freud_sync` (MESSAGE COMMAND) (OWNER ONLY) - force-syncs the bot's slash commands to
 whatever guild it's connected to
 - `/config admin_role` (OWNER ONLY) - Set the role that 'admin' members will have
 - `/config verified_role` (ADMIN ONLY) - Set the role that's given to verified members
 - `/config verification_channel` (ADMIN ONLY) - Set the channel in which the `/verify`
 command may be used
 - `/config logging_channel` (ADMIN ONLY) - Set the channel into which log messages will be
 posted

#### Calendar

 - `/calendar` - Build an image to show your calendar for this week
 - `/course enroll` - Set yourself as enrolled in a course
 - `/course drop` - Unset yourself as enrolled in a course
 - `/course overview` - Send a list of all courses you are enrolled in
 - `/course add` (ADMIN ONLY) - Add an available course and scrape its lecture dates
 - `/course remove` (ADMIN ONLY) - Remove an available course
 - `/course list` (ADMIN ONLY) - List all available Courses

#### Verification

 - `/verify <email>` - Sends an email to `<email>` containing a verification
 code the user can then use in the `/verify <code>` command
 - `/verify <code>` - Checks if the supplied code is valid for a given user
 and gives them the 'Verified' role if it is.

#### Random

- `/mommy` - You can figure this one out for yourself

#### Link Shortcuts (DEPRECATED)

 - `/drive <course>` - Send a link to a google drive for that course

### Hooks

 - on mention: Responds to the message with a random Freud quote

## Running

The latest release of the bot can be ran using `make`, this will pull the
latest version from https://ghcr.io.

The bot can also be built localy using `make dev`, this will use the provided
[dockerfile](Dockerfile) to build and run a local image.
