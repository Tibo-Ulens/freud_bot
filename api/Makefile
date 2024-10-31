.PHONY: all fmt lint

CLIPPY_ALLOW = -A clippy::wildcard-imports
CLIPPY_FLAGS = -W clippy::pedantic $(CLIPPY_ALLOW) -D warnings

lint:
	cargo +nightly clippy --all-targets -- $(CLIPPY_FLAGS)

fmt:
	cargo +nightly fmt
