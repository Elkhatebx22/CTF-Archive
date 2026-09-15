FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

COPY . /app

EXPOSE 5335/udp
EXPOSE 53535/udp

RUN adduser --disabled-password dnsuser
USER dnsuser

CMD ["python", "main.py"]
