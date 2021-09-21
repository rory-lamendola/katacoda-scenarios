#!/bin/bash
#
# generate an alembic revision

set -euo pipefail

message=${1:-}
if [[ -z $message ]]; then
    echo "Usage: $(basename "$0") <message>" 1>&2
    exit 1
fi

component_name="interviews"
inner_directory="interviews"
topdir=$(git rev-parse --show-toplevel)

# 

cd "$topdir/$component_name"
docker-compose up -d postgres vault vault-sync
postgres_container_name="$component_name"_postgres_1
vault_sync_container_name="$component_name"_vault-sync_1
make venv
. venv/bin/activate

for container in "$postgres_container_name" "$vault_sync_container_name"; do
    echo -n "Waiting for container $container to be healthy" 1>&2
    while [[ $(docker inspect "$container" -f '{{.State.Health.Status}}') != 'healthy' ]]; do
        echo -n . 1>&2
        sleep 3
    done
done

(
    export VAULT_ADDR=http://localhost:8200
    export VAULT_TOKEN=vault-token

    cd "$inner_directory"

    if [[ -n "$(find alembic/versions -name \*.py)" ]]; then
        alembic upgrade head
    else
        echo "No Alembic versions found, skipping upgrade" 1>&2
    fi

    alembic revision --autogenerate -m "$message"
)

docker-compose down

# 
