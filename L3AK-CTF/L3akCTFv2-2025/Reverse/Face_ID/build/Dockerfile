FROM python:3.9-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY final /app/final
COPY user.db /app/user.db
COPY app.py /app/app.py
COPY flag.txt /app/flag.txt

RUN chmod +x /app/final

RUN apt-get update && apt-get install -y socat && apt-get clean

ARG APP_PORT=12345
ENV APP_PORT=${APP_PORT}
EXPOSE ${APP_PORT}

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "app.py"]