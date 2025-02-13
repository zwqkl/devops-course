# Используем официальный образ Python
FROM python:3.12.4

# Устанавливаем необходимые системные библиотеки
RUN apt-get update && apt-get install -y libpq-dev python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения и файл с переменными среды
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду для запуска приложения
CMD ["python3", "devops_python_bot.py"]
