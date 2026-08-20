ARG BUILD_FROM
FROM $BUILD_FROM

# Installation des dépendances système
RUN apk add --no-cache \
    python3 \
    py3-pip \
    sqlite

# Copie de l'application
COPY rootfs/app /app
WORKDIR /app

# Installation des dépendances Python
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copie du script de démarrage
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]