FROM python:slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
	&& apt install -y libpq5 libpq-dev python3-dev gcc \
	&& rm -rf /var/lib/apt/lists/*

# Disable pip cache and poetry venvs
ENV PIP_NO_CACHE_DIR=false \
	POETRY_VIRTUALENVS_CREATE=false

# Get poetry
RUN pip install -U poetry

WORKDIR /freud_bot

# Install deps
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY . .

CMD [ "python3", "-m", "bot" ]
