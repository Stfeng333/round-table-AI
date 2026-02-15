feat
FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y

FROM node:lts AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y python3-venv \
    && rm -rf /var/lib/apt/lists/*
main

WORKDIR /app

COPY requirements.txt .
feat

RUN python3 -m venv /opt/venv && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app"]

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

COPY --from=frontend-build /frontend/dist ./frontend/dist

CMD ["gunicorn", "--log-level", "debug", "app_sam:app"]
main
