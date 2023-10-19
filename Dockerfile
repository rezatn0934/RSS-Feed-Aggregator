FROM python:3.11.0

LABEL maintainer="Reza Teymouri Nejad <rezatn0934@gmail.com>" \
      description="Dockerfile for a Python application using Python 3.11" \
      version="1.0" \
      source="https://github.com/rezatn0934/RSS-Feed-Aggregator.git"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y gettext


COPY . /code/

EXPOSE 8000

CMD python manage.py makemessages --all && \
    python manage.py compilemessages && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
