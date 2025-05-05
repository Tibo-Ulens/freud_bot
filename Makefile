.PHONY: all dev fmt lint setup dbd migrate psql chd redis down

all:
	docker compose up --build freudbot freudbot_webconfig

dev: fmt
	docker compose up --build freudbot_dev freudbot_webconfig_dev

fmt:
	black .

lint:
	pylint --disable missing-module-docstring bot/**/*.py

setup:
	chmod +x ./bin/setup.sh
	./bin/setup.sh
	$(MAKE) migrate

dbd:
	docker compose up --build freudbot_db --remove-orphans -d

migrate: dbd
	PGPASSWORD=postgres_password alembic upgrade head
	docker compose down

psql: dbd
	docker exec -it freudbot_db psql -d freudbot -h freudbot_db -U postgres_user

chd:
	docker compose up --build freudbot_cache --remove-orphans -d

redis: chd
	docker exec -it freudbot_cache redis-cli -h freudbot_cache -p 6379

down:
	docker compose down
