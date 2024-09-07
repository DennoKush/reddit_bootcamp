#!/bin/bash
set -e

# Check if necessary environment variables are set
if [ -z "POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_PASSWORD" ]; then
  echo "Environment variables POSTGRES_USER, POSTGRES_DB, and POSTGRES_PASSWORD must be set."
  exit 1
fi

# Function to check if a database exists
database_exists() {
  psql -U "POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$1"
}

# Function to check if a role exists
role_exists() {
  psql -U "POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$1'" | grep -q 1
}

# Retry logic for PostgreSQL readiness
until psql -h localhost -U "POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - executing command"

# Create database if it doesn't exist
if ! database_exists "reddit_dwh"; then
  psql -v ON_ERROR_STOP=1 --username "POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
      CREATE DATABASE reddit_dwh;
EOSQL
  echo "Database 'reddit_dwh' created."
else
  echo "Database 'reddit_dwh' already exists."
fi

# Create roles and user if they don't exist
if ! role_exists "postgres"; then
  psql -v ON_ERROR_STOP=1 --username "POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
      CREATE ROLE postgres WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';
EOSQL
  echo "Role 'postgres' created."
else
  echo "Role 'postgres' already exists."
fi

if ! role_exists "postgres"; then
  psql -v ON_ERROR_STOP=1 --username "POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
      CREATE ROLE postgres WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '$POSTGRES_PASSWORD';
EOSQL
  echo "Role 'postgres' created."
else
  echo "Role 'postgres' already exists."
fi

if ! role_exists "POSTGRES_USER"; then
  psql -v ON_ERROR_STOP=1 --username "POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
      CREATE USER POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
      GRANT ALL PRIVILEGES ON DATABASE reddit_dwh TO POSTGRES_USER;
EOSQL
  echo "User 'POSTGRES_USER' created and granted privileges on 'reddit_dwh' database."
else
  echo "User 'POSTGRES_USER' already exists."
fi

