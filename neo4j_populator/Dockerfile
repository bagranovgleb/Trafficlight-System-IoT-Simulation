FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir mysql-connector-python py2neo

CMD ["python", "populate_neo4j.py"]
