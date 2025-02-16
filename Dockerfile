FROM python:3.12-slim

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /server

COPY pyproject.toml poetry.lock README.md /server/

RUN  poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port 8000"]
