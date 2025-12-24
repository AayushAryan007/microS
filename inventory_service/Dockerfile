# Python base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirement.txt /app/requirement.txt
RUN pip install --upgrade pip && pip install -r /app/requirement.txt

COPY . /app

EXPOSE 8003
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]