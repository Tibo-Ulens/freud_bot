#
# BUILD
#

FROM clux/muslrust:1.86.0-stable AS build

RUN cargo new --vcs none --bin --edition 2024 freudbot_api
WORKDIR /volume/freudbot_api

COPY ./.cargo ./Cargo.toml ./Cargo.lock ./

# Build and cache dependencies
RUN RUSTFLAGS="-Ctarget-cpu=native --cfg tokio_unstable" cargo build --release --bin freudbot_api

RUN rm -r ./src
RUN rm ./target/x86_64-unknown-linux-musl/release/deps/freudbot_api*

# Copy over actual source code
COPY ./src ./src

# Build source code (dependencies already built)
RUN RUSTFLAGS="-Ctarget-cpu=native --cfg tokio_unstable" cargo build --release --bin freudbot_api

#
# EXECUTION
#

FROM alpine:latest

RUN apk add --no-cache curl

# Healthcheck:
# Attempt to curl (fail silently) the service every 30s,
# fail after 5s without a response,
# retry twice before giving up
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
	CMD curl --fail http://localhost/ || exit 1

WORKDIR /freudbot_api

# Copy over the built binary
COPY \
	--from=build \
	/volume/freudbot_api/target/x86_64-unknown-linux-musl/release/freudbot_api \
	.

CMD [ "./freudbot_api" ]
