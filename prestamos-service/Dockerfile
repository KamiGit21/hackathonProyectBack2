FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app
COPY app ./app

# Arrancar FastAPI (ajusta el módulo si tu main es distinto)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
