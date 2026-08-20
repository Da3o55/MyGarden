#!/usr/bin/with-contenv bashio

bashio::log.info "Démarrage de add-on MyGarden..."

export PERENUAL_API_KEY=$(bashio::config 'perenual_api_key')
export DB_PATH="/data/mygarden.db"

if bashio::services.available "mqtt"; then
    export MQTT_HOST=$(bashio::services mqtt "host")
    export MQTT_PORT=$(bashio::services mqtt "port")
    export MQTT_USER=$(bashio::services mqtt "username")
    export MQTT_PASS=$(bashio::services mqtt "password")
    bashio::log.info "MQTT détecté: host=${MQTT_HOST} port=${MQTT_PORT} user=${MQTT_USER}"
else
    bashio::log.warning "MQTT non disponible !"
fi

mkdir -p /data
cd /app

export PYTHONUNBUFFERED=1

exec /venv/bin/python3 main.py