.PHONY: all fmt migrate down dbd setup

all:
	docker compose up --build freud_bot

dev: fmt
	docker compose up --build freud_bot_dev

fmt:
	black .

setup:
	chmod +x ./bin/setup.sh
	./bin/setup.sh
	$(MAKE) migrate

dbd:
	docker compose up --build freud_bot_db --remove-orphans -d

migrate: dbd
	PGPASSWORD=postgres_password alembic upgrade head
	docker compose down

psql: dbd
	docker exec -it freud_bot_db psql -d freud_bot -h freud_bot_db -U postgres_user

down:
	docker compose down
