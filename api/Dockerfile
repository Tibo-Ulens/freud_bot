#
# BUILD
#

FROM clux/muslrust:1.86.0-stable AS build

RUN cargo new --vcs none --bin --edition 2024 freudbot_api
WORKDIR /volume/freudbot_api

COPY ./.cargo ./Cargo.toml ./Cargo.lock ./

# Build and cache dependencies
RUN RUSTFLAGS="-Ctarget-cpu=native --cfg tokio_unstable" cargo build --bin freudbot_api

RUN rm -r ./src
RUN rm ./target/x86_64-unknown-linux-musl/debug/deps/freudbot_api*

# Copy over actual source code
COPY ./src ./src

# Build source code (dependencies already built)
RUN RUSTFLAGS="-Ctarget-cpu=native --cfg tokio_unstable" cargo build --bin freudbot_api

#
# EXECUTION
#

FROM alpine:latest

# Add curl for healthcheck
RUN apk add --no-cache curl

WORKDIR /freudbot_api

# Copy over the built binary
COPY \
	--from=build \
	/volume/freudbot_api/target/x86_64-unknown-linux-musl/debug/freudbot_api \
	.

CMD [ "./freudbot_api" ]
