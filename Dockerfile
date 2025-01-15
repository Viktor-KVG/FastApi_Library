FROM python:3.11.9-alpine3.19


RUN pip install --upgrade pip

# Копируем файл requirements.txt в контейнер
COPY requirements.txt /FastApi_Library/requirements.txt

# Устанавливаем зависимости
RUN pip install -r /FastApi_Library/requirements.txt

# Копируем весь код в контейнер
COPY . /FastApi_Library

# Устанавливаем рабочую директорию
WORKDIR /FastApi_Library


CMD [ "uvicorn src.main:app --reload" ]

