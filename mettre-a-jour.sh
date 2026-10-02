#!/usr/bin/env bash
# TP Odoo : retour exact a la version de la seance (macOS / Linux).
#   ./mettre-a-jour.sh            derniere version publiee (branche main)
#   ./mettre-a-jour.sh seance-02  version figee d'une seance precise
cd "$(dirname "$0")" || exit 1
CIBLE="${1:-origin/main}"

main() {
  if ! command -v git >/dev/null 2>&1; then
    echo "[ERREUR] Git n'est pas installe (macOS : xcode-select --install ; Linux : sudo apt install git)."
    exit 1
  fi
  if [ ! -d .git ]; then
    echo "[ERREUR] Ce dossier n'a pas ete obtenu avec git clone : git clone https://github.com/M2P-git/tp-odoo.git"
    exit 1
  fi
  echo "============================================================"
  echo " TP Odoo : retour exact a la version de la seance ($CIBLE)"
  echo "============================================================"
  echo "ATTENTION :"
  echo "  - vos modifications dans les fichiers de ce dossier seront EFFACEES ;"
  echo "  - Odoo sera recree : vos saisies dans Odoo seront PERDUES."
  read -r -p "Continuer ? [o/N] " rep
  [ "${rep:-N}" = "o" ] || [ "${rep:-N}" = "O" ] || exit 0

  echo "Etape 1/4 : recuperation des nouveautes (git fetch)"
  git fetch origin --tags || { echo "[ERREUR] Impossible de joindre GitHub."; exit 1; }
  echo "Etape 2/4 : retour a la version de la seance (git reset --hard)"
  git reset --hard "$CIBLE" || { echo "[ERREUR] Version introuvable : $CIBLE"; exit 1; }
  echo "Etape 3/4 : suppression des fichiers en trop (git clean)"
  git clean -fd
  echo "Etape 4/4 : recreation d'Odoo avec la configuration de la seance"
  docker compose down -v
  bash ./demarrer.sh
  exit $?
}
main "$@"
