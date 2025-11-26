FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la app
COPY app/ .

# Exponemos puerto
EXPOSE 5000

# Comando de ejecución
CMD ["python", "app.py"]
