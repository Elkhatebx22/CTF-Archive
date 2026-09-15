FROM python:3.11-slim

ARG DECOY_FLAG="REDACTED"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends mariadb-client netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY flag.txt /tmp/wizard_flag.txt

RUN FLAG_SEED="$(dd if=/dev/urandom bs=16 count=1 2>/dev/null | od -An -tx1 -v | tr -d '[:space:]')" \
    && FLAG_NAME="/flag_${FLAG_SEED}.txt" \
    && cp /tmp/wizard_flag.txt "$FLAG_NAME" \
    && printf '%s\n' "$DECOY_FLAG" > /flag.txt \
    && adduser --disabled-password --no-create-home --gecos app app \
    && mkdir -p /app/cache/previews \
    && chown -R app:app /app/cache \
    && rm -f /tmp/wizard_flag.txt /Dockerfile /docker-compose.yml /app/Dockerfile /app/docker-compose.yml \
    && chmod 444 /flag*.txt

EXPOSE 5000

USER app
CMD ["python", "app.py"]
