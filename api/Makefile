.PHONY: all fmt lint

CLIPPY_FLAGS = -D warnings -W unreachable-pub

lint: fmt
	cargo +nightly clippy -- $(CLIPPY_FLAGS)

fmt:
	cargo +nightly fmt
