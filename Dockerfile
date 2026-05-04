FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp/ \
    ERDDAP_GLIDER_CACHE_DIR=/app/data/glider_grid_cache

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY pyproject.toml README.md ./
COPY src ./src
COPY data/glider_grid_cache ./data/glider_grid_cache

RUN pip install --upgrade pip \
    && pip install .

USER appuser

EXPOSE 8000

CMD ["erddap-grid-mcp"]
