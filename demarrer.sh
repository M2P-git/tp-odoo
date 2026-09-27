#!/usr/bin/env bash
# Démarre l'environnement de TP (macOS / Linux) : ./demarrer.sh
set -euo pipefail
cd "$(dirname "$0")"
if ! docker info >/dev/null 2>&1; then
  echo "[ERREUR] Docker ne répond pas : lancez Docker Desktop (ou le service docker) puis recommencez."
  exit 1
fi
echo "Étape 1/3 : images Docker (environ 1 Go la première fois)"
docker compose pull || echo "[INFO] Téléchargement impossible : utilisation des images déjà présentes."
echo "Étape 2/3 : préparation de la base atlas_micro (première fois : 3 à 8 min)"
if ! docker compose up -d; then
  docker compose logs --no-color init > demarrage.log 2>&1 || true
  echo "[ERREUR] Échec du démarrage. Journal : demarrage.log"
  exit 1
fi
echo "Étape 3/3 : attente du serveur Odoo"
for _ in $(seq 1 60); do
  if curl -s -o /dev/null -m 3 http://localhost:8069/web/login; then
    docker compose logs --no-color init > demarrage.log 2>&1 || true
    echo "[OK] Odoo est prêt : http://localhost:8069  (admin / admin)"
    (command -v open >/dev/null && open http://localhost:8069) || (command -v xdg-open >/dev/null && xdg-open http://localhost:8069) || true
    exit 0
  fi
  sleep 3
done
docker compose logs --no-color init > demarrage.log 2>&1 || true
echo "[ERREUR] Odoo ne répond pas. Journal : demarrage.log"
exit 1
