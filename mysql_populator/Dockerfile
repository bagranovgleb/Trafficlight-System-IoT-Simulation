FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir mysql-connector-python

CMD ["python", "populate_mysql.py"]