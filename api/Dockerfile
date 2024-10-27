# ===============================
#    BACKEND BUILD ENVIRONMENT
# ===============================

FROM rust:latest AS backend_build

# Install nightly
RUN rustup default nightly
RUN rustup update

RUN USER=root cargo new --vcs none --bin freudbot_api
WORKDIR /freudbot_api

COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock
COPY ./.cargo ./.cargo

# "" -> debug compilation
# "release" -> release compilation
ARG IS_RELEASE=""

# Build and cache dependencies
RUN cargo +nightly build --profile ${IS_RELEASE:-dev} --bin freudbot_api
RUN rm ./src/*
RUN rm ./target/${IS_RELEASE:-debug}/deps/freudbot_api*

# Copy over actual source code
COPY ./src ./src
COPY ./migrations ./migrations

# Build source code (dependencies already built)
RUN cargo +nightly build --profile ${IS_RELEASE:-dev} --bin freudbot_api

# ===============================
#      EXECUTION ENVIRONMENT
# ===============================

FROM debian:bookworm-slim

# Install dependency for postgres and healthcheck
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
	&& apt install -y libpq5 curl \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /freudbot_api

# Copy over the built binary
COPY \
	--from=backend_build \
	/freudbot_api/target/${IS_RELEASE:-debug}/freudbot_api \
	.

# Healthcheck:
# Attempt to curl (fail silently) the service every 30s,
# fail after 5s without a response,
# retry twice before giving up
HEALTHCHECK --interval=10m --timeout=5s --retries=2 CMD curl --fail http://localhost/ || exit 1

CMD [ "./freudbot_api" ]
