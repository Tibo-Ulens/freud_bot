# TODO

## General

## Configuration

 - [ ] Add a logging channel and logging handler that can write to discord
 - [ ] Add a hierarchical permissions system and better error messages

# Done

## General

 - [x] Add a github hook to check formatting
 - [x] Add a github action to deploy to dockerhub or ghcr
   - [x] Update the docker compose file to pull from the container repository
         instead of building locally
 - [x] Better logging

## Calendar

 - [x] Select the correct roster link in selenium ~~based on the current time~~
       (eg. semester 1/2, exam period 1/2) (it just scrapes everything and
	   ignores courses it can't find)
## Configuration

 - [x] Add a `/setup` command or a set of `/config {option}` commands to allow
       per-server configuration of stuff like verification channels, what
	   courses to scrape, etc.
 - [x] Add a command to specify an admin/moderator role and a decorator to
       get this role from the database and check if a user has it

