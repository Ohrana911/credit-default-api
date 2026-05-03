FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY models ./models

EXPOSE 5000

CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:5000", "--workers", "2", "api:app"]
