# ============ STAGE 1 : BUILDER ============
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt


# ============ STAGE 2 : RUNTIME ============
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app

# Libs runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

# Créer user non-root + dossier /app
RUN groupadd -r app && useradd -r -g app app \
    && mkdir -p ${APP_HOME} \
    && chown app:app ${APP_HOME}

WORKDIR ${APP_HOME}

# Copier le venv préparé dans le builder
COPY --chown=app:app --from=builder /opt/venv /opt/venv

# Copier le code du projet (inclut entrypoint.sh)
COPY --chown=app:app . .

# Rendre le script exécutable sous ROOT avant de basculer d'utilisateur
RUN chmod +x /app/entrypoint.sh

# Passer en utilisateur non-root pour des raisons de sécurité
USER app

EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
#     CMD python -c "import urllib.request,sys; \
#     sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/', timeout=3).status == 200 else 1)"

# Définir l'entrypoint et la commande par défaut
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]