FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/code

COPY . /usr/src/code

RUN apt update && apt install -y netcat \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/* \
    && chmod +x redis_pg_wait.sh

ENTRYPOINT ["/usr/src/code/redis_pg_wait.sh"]

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "asgi:wsgi", "--bind", "0.0.0.0:5000"]