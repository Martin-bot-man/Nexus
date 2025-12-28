FROM python:3.11-slim

# ------------------------------------------------
# System setup
# ------------------------------------------------
WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------
# Python dependencies
# ------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------
# Application source
# ------------------------------------------------
COPY src/ ./src/

# ------------------------------------------------
# Runtime
# ------------------------------------------------
EXPOSE 8000

# 🚪 Start the API GATEWAY (not the core app)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
