FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 KG_DATA=/app/data/triples.csv
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY data ./data
RUN pip install --no-cache-dir . && useradd -m app
USER app
ENTRYPOINT ["python", "-m", "kg_agent"]
