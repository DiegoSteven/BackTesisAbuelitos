# Usar imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar todo el contenido de la aplicación
COPY . .

# Establecer PYTHONPATH
ENV PYTHONPATH=/app

# Exponer el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación con Flask
CMD ["python", "app/app.py"]
