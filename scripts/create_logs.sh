#!/bin/bash
set -e

# Check if necessary environment variables are set
if [ -z "$AIRFLOW_USER" ] || [ -z "$AIRFLOW_DB" ] || [ -z "$AIRFLOW_PASS" ]; then
  echo "Environment variables AIRFLOW_USER, AIRFLOW_DB, and AIRFLOW_PASS must be set."
  exit 1
fi

# Function to check if a database exists
database_exists() {
  psql -U "$AIRFLOW_USER" -lqt | cut -d \| -f 1 | grep -qw "$1"
}

# Function to check if a role exists
role_exists() {
  psql -U "$AIRFLOW_USER" -d "$AIRFLOW_DB" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$1'" | grep -q 1
}

# Retry logic for PostgreSQL readiness
until psql -h localhost -U "$AIRFLOW_USER" -d "$AIRFLOW_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - executing command"

# Create database if it doesn't exist
if ! database_exists "airflow_logs"; then
  psql -v ON_ERROR_STOP=1 --username "$AIRFLOW_USER" --dbname "$AIRFLOW_DB" <<-EOSQL
      CREATE DATABASE airflow_logs;
EOSQL
  echo "Database 'airflow_logs' created."
else
  echo "Database 'airflow_logs' already exists."
fi

# Create roles and user if they don't exist
if ! role_exists "airflow"; then
  psql -v ON_ERROR_STOP=1 --username "$AIRFLOW_USER" --dbname "$AIRFLOW_DB" <<-EOSQL
      CREATE ROLE airflow WITH LOGIN PASSWORD '$AIRFLOW_PASS';
EOSQL
  echo "Role 'airflow' created."
else
  echo "Role 'airflow' already exists."
fi

if ! role_exists "postgres"; then
  psql -v ON_ERROR_STOP=1 --username "$AIRFLOW_USER" --dbname "$AIRFLOW_DB" <<-EOSQL
      CREATE ROLE postgres WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '$AIRFLOW_PASS';
EOSQL
  echo "Role 'postgres' created."
else
  echo "Role 'postgres' already exists."
fi

if ! role_exists "airflow_user"; then
  psql -v ON_ERROR_STOP=1 --username "$AIRFLOW_USER" --dbname "$AIRFLOW_DB" <<-EOSQL
      CREATE USER airflow_user WITH PASSWORD '$AIRFLOW_PASS';
      GRANT ALL PRIVILEGES ON DATABASE airflow_logs TO airflow_user;
EOSQL
  echo "User 'airflow_user' created and granted privileges on 'airflow_logs' database."
else
  echo "User 'airflow_user' already exists."
fi

# Additional debugging information
psql -U "$AIRFLOW_USER" -d "$AIRFLOW_DB" -c '\du'
psql -U "$AIRFLOW_USER" -d "$AIRFLOW_DB" -c '\l'