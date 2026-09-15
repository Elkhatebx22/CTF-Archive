FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    hashcat \ 
    python3 \
    python3-pip \
    socat \
    && apt-get clean

RUN useradd -ms /bin/bash player

COPY flag.txt /home/player
COPY hash.txt /home/player
COPY cat-whisperer.py /home/player

USER player
WORKDIR /home/player

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 cat-whisperer.py"]
