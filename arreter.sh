#!/usr/bin/env bash
cd "$(dirname "$0")"
docker compose --profile sql stop
echo "Arrêté. Les données sont conservées ; ./demarrer.sh pour reprendre."
