#!/bin/sh

# Setup script to ensure the development environment is properly configured
# for FreudBot

set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel)
VENV_PATH="${PROJECT_ROOT}/venv"
HOOKS_PATH="${PROJECT_ROOT}/.hooks"
HOOKS="${HOOKS_PATH}/*"
GIT_HOOKS_PATH="${PROJECT_ROOT}/.git/hooks"

echo "setting up FreudBot development environment"
echo ""

echo -n "checking if poetry is installed..."
if [ ! -x $(command -v poetry) ]; then
	echo ""
	1>&2 echo "ERROR: poetry is not installed"
	1>&2 echo "see https://python-poetry.org/docs/ for installation instructions"
	exit 1
fi
echo " OK"

echo -n "checking if docker is installed..."
if [ ! -x $(command -v docker) ]; then
	echo ""
	1>&2 echo "ERROR: docker is not installed"
	1>&2 echo "please install docker from your distro's application repository"
	exit 1
fi
echo " OK"

echo -n "checking if docker compose is installed..."
docker compose > /dev/null
if [ "$?" -ne "0" ]; then
	echo ""
	1>&2 echo "ERROR: docker compose is not installed"
	1>&2 echo "see https://docs.docker.com/compose/ for installation instructions"
	exit 1
fi
echo " OK"

if [ ! -d "${VENV_PATH}" ]; then
	echo "WARNING: you are not in a virtual environment"
	echo "any dependencies needed for this project will be installed globally"
	read -p "do you want to continue? [y/n]" yn

	while true; do
		case ${yn} in
			[Yy]* ) break ;;
			[Nn]* ) exit 1 ;;
			* ) break ;;
		esac
	done
fi

echo "installing dependencies..."
poetry install > /dev/null
tput sc
tput cuu 1
tput cuf 26
echo " OK"
tput rc

echo "symlinking github hooks..."
cursor_v_offset=1
for hook in ${HOOKS}; do
	hook_file=$(basename "${hook}")
	echo "  ${hook} -> ${GIT_HOOKS_PATH}/${hook_file}"
	ln -s -f "${hook}" "${GIT_HOOKS_PATH}/${hook_file}"
	chmod +x "${GIT_HOOKS_PATH}/${hook_file}"

	cursor_v_offset=$((cursor_v_offset+1))
done
tput sc
tput cuu ${cursor_v_offset}
tput cuf 26
echo " OK"
tput rc

echo "creating docker volumes..."
docker volume create freud_bot_data > /dev/null
tput sc
tput cuu 1
tput cuf 26
echo " OK"
tput rc

echo "creating secrets..."
mkdir -p secrets
read -p "enter discord bot token: " discord_token
read -p "enter smtp username: " smtp_user
read -p "enter smtp password: " smtp_pwd
read -p "enter discord client ID: " client_id
read -p "enter discord client secret: " client_secret
echo "${discord_token}" > "${PROJECT_ROOT}/secrets/discord_token.txt"
echo "${smtp_user}" > "${PROJECT_ROOT}/secrets/smtp_credentials.txt"
echo "${smtp_pwd}" >> "${PROJECT_ROOT}/secrets/smtp_credentials.txt"
echo "${client_id}" >> "${PROJECT_ROOT}/secrets/discord_oauth_credentials.txt"
echo "${client_secret}" >> "${PROJECT_ROOT}/secrets/discord_oauth_credentials.txt"
tput sc
tput cuu 6
tput cuf 19
echo " OK"
tput rc
