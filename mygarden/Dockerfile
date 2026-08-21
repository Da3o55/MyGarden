ARG BUILD_FROM
FROM $BUILD_FROM

# Installation Python + dépendances système
RUN apk add --no-cache \
    python3 \
    py3-pip \
    sqlite \
    && python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"

COPY rootfs/app /app
WORKDIR /app

RUN /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]