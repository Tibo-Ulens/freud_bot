.PHONY: all fmt migrate down dbd setup

all: fmt
	docker compose up --build

fmt:
	black .

setup:
	chmod +x ./bin/setup.sh
	./bin/setup.sh

dbd:
	docker compose up --build freud_bot_db --remove-orphans -d

migrate: dbd
	PGPASSWORD=postgres_password alembic upgrade head
	docker compose down

psql: dbd
	docker exec -it freud_bot_db psql -d freud_bot -h freud_bot_db -U postgres_user

down:
	docker compose down
