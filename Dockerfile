FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline ./pipeline

FROM base AS test
COPY tests ./tests
COPY pytest.ini .
CMD ["python", "-m", "pytest"]

FROM base AS runtime

RUN mkdir -p \
    data/raw \
    data/features \
    data/models \
    data/predictions \
    data/quality

EXPOSE 8501

CMD ["python", "-m", "pipeline.simulator"]