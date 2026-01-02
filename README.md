# Note API

## Description

A simple API for managing notes. It allows users to create, read, update, and delete notes.

## Installation

### Native

To install this project, you need [uv](https://docs.astral.sh/uv/).

```bash
uv venv
source .venv/bin/activate
uv sync
cp .env.example .env
```

Then populate the `.env` file with required values and set up PostgreSQL.

### Running Migrations

```bash
alembic upgrade head
```

## Running The App
```bash
# development
fastapi dev

# production mode
fastapi run
```

## OpenAPI

This API provides [OpenAPI](https://www.openapis.org/what-is-openapi) documentation at:
- `API_URL/docs`
- `API_URL/redoc`

## Stay In Touch

Author - [Piotr Orczykowski](mailto:orczykowski.peter@gmail.com)

## License

This project is [MIT licensed](LICENSE).
