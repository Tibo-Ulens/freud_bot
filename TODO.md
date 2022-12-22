# TODO

## Calendar

 - [ ] Select the correct roster link in selenium based on the current time
       (eg. semester 1/2, exam period 1/2)
 - [ ] Automatically fetch a list of all courses for the current period instead
       of needing to use `/course add`

## Configuration

 - [ ] Add a `/setup` command or a set of `/config {option}` commands to allow
       per-server configuration of stuff like verification channels, what
	   courses to scrape, etc.

# Done

## General

 - [x] Add a github hook to check formatting
 - [x] Add a github action to deploy to dockerhub or ghcr
   - [x] Update the docker compose file to pull from the container repository
         instead of building locally
