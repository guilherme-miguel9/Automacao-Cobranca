# Base image
FROM python:3.11-slim

# Evita criação de arquivos .pyc e força log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho no container
WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos do projeto
COPY . .

# Execução padrão
CMD ["python", "main.py"]
