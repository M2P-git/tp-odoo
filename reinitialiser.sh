#!/usr/bin/env bash
cd "$(dirname "$0")"
read -r -p "Effacer toutes les modifications et recréer le jeu initial ? [o/N] " rep
[ "${rep:-N}" = "o" ] || [ "${rep:-N}" = "O" ] || exit 0
docker compose --profile sql down -v
./demarrer.sh
