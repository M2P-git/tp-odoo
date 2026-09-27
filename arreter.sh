#!/usr/bin/env bash
cd "$(dirname "$0")"
docker compose stop
echo "Arrêté. Les données sont conservées ; ./demarrer.sh pour reprendre."
