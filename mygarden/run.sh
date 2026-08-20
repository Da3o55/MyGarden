#!/usr/bin/with-contenv bashio

bashio::log.info "Démarrage de MyGarden..."

export PERENUAL_API_KEY=$(bashio::config 'perenual_api_key')
export DB_PATH="/data/mygarden.db"

mkdir -p /data

cd /app
/venv/bin/python3 main.py