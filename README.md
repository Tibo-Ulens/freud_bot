# FreudBot

UGent Psychology Discord server bot

## Features

Unless stated otherwise all commands are slash commands

### Commands

#### Configuration

 - `$freud_sync` - MESSAGE COMMAND - force-syncs the bot's slash commands to
 whatever guild it's connected to
 - `/config verified_role` - Set the role that's given to verified members
 - `/config verification_channel` - Set the channel in which the `/verify`
 command may be used

#### Verification

 - `/verify <email>` - Sends an email to `<email>` containing a verification
 code the user can then use in the `/verify <code>` command
 - `/verify <code>` - Checks if the supplied code is valid for a given user
 and gives them the 'Verified' role if it is.

### Hooks

 - on mention: Responds to the message with a random Freud quote

## Running

The latest release of the bot can be ran using `make`, this will pull the
latest version from https://ghcr.io.

The bot can also be built localy using `make dev`, this will use the provided
[dockerfile](Dockerfile) to build and run a local image.

## Development

Database interaction and ORM capabilities are handled by SQLAlchemy using its
async functions. \
Note that SQLAlchemy itself does not create any tables and/or run migrations,
these are handled by [Alembic](#migrations). As such if changes to the database
schema are required they should executed using Alembic, and the SQLAlchemy code
can be updated accordingly.

The [`models`](bot/models/__init__.py) module defines a global session_factory
object which can be used to retrive database session instances, these are
intended to be used in context managers.

### Versioning

Whenever a commit with a version tag of the form v.{major}.{minor}.{patch} is
pushed a GitHub action will automatically create a new release draft for that
version.

### Migrations

Migrations are managed using Alembic, then can be created using
`alembic revision -m <name>`.
Migrations can be ran using `make migrate` which will spin up the database
container, run the migrations, and then stop the container again.

### Utilities

 - `make setup` will create/download the stuff needed to work on the project
 - `make dbd` will spin up a headless instance of the database container
 - `make psql` will start a psql instance in the database container
 - `make down` will stop all running containers
