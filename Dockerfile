# Utiliser une image de base Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements.txt
COPY requirements.txt requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Définir la variable d'environnement pour Flask
ENV FLASK_APP=app.py

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Lancer l'application Flask
CMD ["flask", "run", "--host=0.0.0.0"]
