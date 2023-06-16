FROM python:3.10.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
	&& apt install -y libpq5 libpq-dev python3-dev gcc wget firefox-esr \
	&& rm -rf /var/lib/apt/lists/*

# Disable pip cache and poetry venvs
ENV PIP_NO_CACHE_DIR=false \
	POETRY_VIRTUALENVS_CREATE=false

# Get poetry
RUN pip install -U poetry

# Get selenium webdriver
RUN wget \
	https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
RUN tar xvzf geckodriver-v0.31.0-linux64.tar.gz
RUN rm -rf geckodriver-v0.31.0-linux64.tar.gz
RUN mv geckodriver /usr/bin && chmod +x /usr/bin/geckodriver

WORKDIR /freud_bot

# Install deps
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

COPY . .

CMD [ "python3", "-m", "bot" ]
