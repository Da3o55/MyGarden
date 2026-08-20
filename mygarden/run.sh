#!/bin/bash
set -x  # Affiche chaque commande exécutée

echo "=== DÉMARRAGE MYGARDEN ===" >&2
echo "Date: $(date)" >&2
echo "User: $(whoami)" >&2
echo "PWD: $(pwd)" >&2

echo "=== Test Python ===" >&2
/venv/bin/python3 --version 2>&1 || echo "ERREUR: Python pas trouvé!" >&2

echo "=== Test fichiers ===" >&2
ls -la /app/ 2>&1 || echo "ERREUR: /app/ n'existe pas!" >&2
test -f /app/main.py && echo "✓ main.py existe" >&2 || echo "✗ main.py MANQUANT!" >&2

echo "=== Environnement ===" >&2
env | grep -E "(PERENUAL|MQTT|DB_PATH|PATH)" >&2

echo "=== LANCEMENT PYTHON ===" >&2
cd /app
exec /venv/bin/python3 main.py 2>&1