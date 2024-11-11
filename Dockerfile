FROM python:3.9-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y sshpass ssh

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app.py .

# Exposer le port par défaut pour Flask
EXPOSE 8080

# Démarrer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
