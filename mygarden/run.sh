#!/usr/bin/with-contenv bashio

bashio::log.info "Démarrage de MyGarden..."

# Récupération de la config
export PERENUAL_API_KEY=$(bashio::config 'perenual_api_key')
export DB_PATH="/data/mygarden.db"

# Création du dossier data si nécessaire
mkdir -p /data

cd /app
python3 main.py