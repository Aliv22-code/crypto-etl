FROM python:3.11-slim

# system packages needed by psycopg2 and dbt
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy deps first — cached layer (faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

# copy project files
COPY pipelines/   ./pipelines/
COPY dbt_project/ ./dbt_project/
COPY sql/         ./sql/

# run the Prefect flow when container starts
CMD ["python", "-m", "pipelines.flow"]