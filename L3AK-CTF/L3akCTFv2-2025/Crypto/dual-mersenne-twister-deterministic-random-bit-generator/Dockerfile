FROM python:3.13-slim
RUN apt-get update && apt-get install -y socat
RUN useradd -ms /bin/bash player
COPY dual_mt_drbg.py /home/player
COPY flag.py /home/player
USER player
WORKDIR /home/player

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 dual_mt_drbg.py"]