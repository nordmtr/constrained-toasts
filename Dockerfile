FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock /app/
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY src/ /app/src/

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-u", "src/bot.py"]
