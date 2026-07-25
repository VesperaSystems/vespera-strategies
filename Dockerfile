# Vespera signal runner — small CPU-only image.
# Runs the watchlist strategies and posts signals to Mission Control.
#
#   docker build -t vespera-runner .
#   docker run -e VESPERA_API_URL=... -e VESPERA_API_KEY=... vespera-runner
#
# Works as-is on Azure Container Apps Jobs, a Nebius VM cron, or any
# container scheduler.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY vespera_strategies ./vespera_strategies
COPY runner.py ./

RUN pip install --no-cache-dir .

CMD ["python", "runner.py"]
