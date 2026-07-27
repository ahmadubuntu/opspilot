# Bootstrap Guide

This document explains how to bootstrap a fresh development environment.

## Requirements

- Ubuntu 24.04+
- Docker
- Docker Compose
- Git
- Python 3.11+
- uv
- LM Studio

## Clone

git clone <repository>

cd opspilot

## Environment

cp .env.example .env

Edit the values if needed.

## Start Open WebUI

docker-compose up -d

Verify

docker ps

Open

http://localhost:3000

## Python Environment

uv sync

## Verify

uv run python --version

## Run Tests

uv run pytest

## Format

uv run ruff format .

## Lint

uv run ruff check .

## Type Check

uv run mypy .

## Project Structure

README.md

PROJECT_PRINCIPLES.md

docs/

.ai/

plugins/

opspilot/

tests/

workspace/

## Development Flow

1. Create branch

2. Implement feature

3. Add tests

4. Update documentation

5. Update .ai files

6. Commit

7. Merge
