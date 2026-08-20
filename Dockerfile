ARG BUILD_FROM=python:3.11-slim
FROM ${BUILD_FROM}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mygarden ./mygarden
COPY rootfs ./rootfs
COPY www ./www
EXPOSE 8099
CMD ["python", "/app/rootfs/mygarden.py"]
