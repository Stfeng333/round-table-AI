# Stage 1: Build frontend
FROM node:lts AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build

# Stage 2: Python app
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

COPY --from=frontend-build /frontend/dist ./frontend/dist

CMD ["gunicorn", "--log-level", "debug", "app_sam:app"]
