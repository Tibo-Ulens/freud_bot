.PHONY: all fmt

all: fmt
	docker-compose up --build

fmt:
	black .
