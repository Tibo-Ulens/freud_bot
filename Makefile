.PHONY: all

all: format
	docker-compose up --build

format:
	black .
