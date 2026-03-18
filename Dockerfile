FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install aiogram==3.1.0

CMD ["python", "bot.py"]
