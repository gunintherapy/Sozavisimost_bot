# Используем официальный Python 3.11
FROM python:3.11-slim

# Обновляем pip и ставим системные библиотеки для aiohttp
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .

# Ставим зависимости
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Запуск бота
CMD ["python", "bot.py"]
