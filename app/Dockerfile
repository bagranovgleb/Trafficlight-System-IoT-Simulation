FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask mysql-connector-python pymongo py2neo


EXPOSE 5000

CMD ["python", "app.py"]
