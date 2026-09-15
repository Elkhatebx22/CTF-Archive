FROM python:3.10-slim AS prebuild

RUN apt-get update && apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pycryptodome

RUN mkdir -p /app
WORKDIR /app

COPY chall.py flag.txt ./

FROM pwn.red/jail

COPY --from=prebuild / /srv

COPY entrypoint.sh /srv/app/run
COPY flag.txt /srv/app/flag.txt
COPY chall.py /srv/app/chall.py

ENV JAIL_PIDS=40 JAIL_MEM=100M JAIL_TIME=3600
