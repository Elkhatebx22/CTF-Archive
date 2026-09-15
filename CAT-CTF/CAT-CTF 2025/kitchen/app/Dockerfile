FROM python:3.11-slim

ENV flag=catf{@!_Stacked_Buns_&_Beef_@!_Hunger_Levels_MAX}

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
