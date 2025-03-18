FROM ghcr.io/astral-sh/uv:0.6.6-python3.13-alpine

RUN adduser -S app && \
    mkdir /app && \
    chown app /app

USER app

ADD . /app

WORKDIR /app

RUN export PYTHONPATH=/app/src:$PYTHONPATH && \
    uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "--directory", "src", "main.py"]
