FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends --only-upgrade liblzma5 && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 10001 --shell /usr/sbin/nologin --no-create-home appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r requirements.txt && pip uninstall -y pip setuptools wheel

COPY app/ ./app/
RUN chown -R appuser:appuser /app
USER appuser

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"

CMD ["python", "-m", "app.main"]
