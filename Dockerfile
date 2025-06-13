FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PORT=8080

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", ":8080", "run:app"]
