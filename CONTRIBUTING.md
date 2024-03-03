# Welcome to the FreudBot development guide

## Overview

Database interaction and ORM capabilities are handled by SQLAlchemy using its
async functions. \
Note that SQLAlchemy itself does not create any tables and/or run migrations,
these are handled by [Alembic](#migrations). As such if changes to the database
schema are required they should executed using Alembic, and the SQLAlchemy code
can be updated accordingly.

The [`models`](bot/models/__init__.py) module defines a global session_factory
object which can be used to retrive database session instances, these are
intended to be used in context managers.

## Getting started

You will need to be on a *nix operating system, with docker, docker compose,
make, python, and poetry installed.

You can set up the project locally by running `make setup`.

### Migrations

Migrations are managed using Alembic, then can be created using
`alembic revision -m <name>`.
Migrations can be ran using `make migrate` which will spin up the database
container, run the migrations, and then stop the container again.

### Utilities

 - `make` will pull the latest docker image from GHCR and run it
 - `make dev` will build a docker image from the local code and run it
 - `make down` will stop all running containers
 - `make dbd` will spin up a headless instance of the database container
 - `make chd` will spin up a headless instance of the cache container
 - `make psql` will start a psql instance in the database container
 - `make redis` will start a redis CLI instance in the cache container
 - `make setup` will create/download the stuff needed to work on the project

### Issues

If you spot a problem in the bot, please create an issue
[here](https://github.com/Tibo-Ulens/freud_bot/issues/new)

### Adding new functionality

If you would like for new functionality to be added to the bot, please open an
issue or create a
[pull request](https://github.com/Tibo-Ulens/freud_bot/compare) if you have
written your own implementation.

### Adding new commands

All commands are wrapped in 'Cogs' in the [extensions](bot/extensions/) folder.
Any new commands should be added to an existing cog, or have their own, new,
cog.
