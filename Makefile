.PHONY: all dev fmt lint setup dbd migrate psql chd redis down

all:
	docker compose up --build freud_bot freud_bot_webconfig

dev: fmt
	docker compose up --build freud_bot_dev freud_bot_webconfig_dev

fmt:
	black .

lint:
	pylint --disable missing-module-docstring bot/**/*.py

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

chd:
	docker compose up --build freud_bot_cache --remove-orphans -d

redis: chd
	docker exec -it freud_bot_cache redis-cli -h freud_bot_cache -p 6379

down:
	docker compose down
