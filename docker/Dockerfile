FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY arb_bot ./arb_bot
COPY .env ./

ENV PYTHONPATH=/app/arb_bot
CMD ["python", "-m", "app.main"]
