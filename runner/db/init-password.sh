#!/bin/bash
set -e

# This script runs during database initialization
# It sets up password authentication for external connections

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Ensure password is set correctly
    ALTER USER postgres WITH PASSWORD 'postgres';
EOSQL

echo "Password authentication configured for external connections"
