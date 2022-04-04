# Docker-команда FROM указывает базовый образ контейнера
# Наш базовый образ - это Linux с предустановленным python-3.7
FROM python:3.9
# Скопируем файл с зависимостями в контейнер
#WORKDIR /app#

COPY requirements.txt .
# Установим зависимости внутри контейнера
RUN pip3 install -r requirements.txt
# Скопируем остальные файлы в контейнер
COPY . .
# разрешаем наш скрипт на исполнение операционной системой
RUN chmod +x run.sh
# запускаем скрипт
EXPOSE 8080
CMD ["python", "./main.py"]
#CMD ["./run.sh"]