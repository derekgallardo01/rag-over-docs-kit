# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --quiet pytest

# Default command runs the scripted demo (workplace corpus). Override:
#   docker run --rm <image> python cli.py
#   docker run --rm <image> python evals/run.py
#   docker run --rm <image> python evals/run.py golden-tech.json data-tech
#   docker run --rm <image> python -m pytest -q
CMD ["python", "run.py"]
