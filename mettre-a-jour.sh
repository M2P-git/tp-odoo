#!/usr/bin/env bash
# TP Odoo : mise a jour vers une seance (macOS / Linux).
#   ./mettre-a-jour.sh        le numero de la seance est demande (liste affichee)
#   ./mettre-a-jour.sh 4      numero donne directement ; 3.3 = seance 3, reprise a la mission 3
cd "$(dirname "$0")" || exit 1

# Tout est dans une fonction : bash la lit en entier avant de l'executer, elle reste valide
# meme si ce fichier est remplace par git reset.
main() {
  local choix="${1:-}" defaut rep
  if ! command -v git >/dev/null 2>&1; then
    echo "[ERREUR] Git n'est pas installe (macOS : xcode-select --install ; Linux : sudo apt install git)."
    exit 1
  fi
  if [ ! -d .git ]; then
    echo "[ERREUR] Ce dossier n'a pas ete obtenu avec git clone : git clone https://github.com/M2P-git/tp-odoo.git"
    exit 1
  fi

  echo "Recuperation des seances publiees (git fetch)..."
  git fetch origin --tags || { echo "[ERREUR] Impossible de joindre GitHub."; exit 1; }
  defaut=$(git show origin/main:SEANCE | tr -d ' \r\n')
  echo "============================================================"
  echo " TP Odoo : choisir la seance"
  echo "============================================================"
  echo " Numero   Ce que vous obtenez"
  git show origin/main:seances.txt | grep -v '^#'
  echo
  if [ -z "$choix" ]; then
    read -r -p "Numero donne par l'enseignant (Entree = $defaut) : " choix
  fi
  choix="${choix:-$defaut}"
  choix="${choix/,/.}"
  if ! git show origin/main:seances.txt | grep -q "^${choix//./\\.} "; then
    echo "[ERREUR] Numero inconnu : $choix. Relancez et tapez un numero de la liste."
    exit 1
  fi

  echo
  echo "Seance choisie : $choix"
  echo "ATTENTION :"
  echo "  - vos modifications dans les fichiers de ce dossier seront EFFACEES ;"
  echo "  - Odoo sera recree : vos saisies dans Odoo seront PERDUES."
  read -r -p "Continuer ? [o/N] " rep
  [ "${rep:-N}" = "o" ] || [ "${rep:-N}" = "O" ] || exit 0

  echo "Etape 1/4 : derniere version publiee (git reset --hard)"
  git reset --hard origin/main || { echo "[ERREUR] Mise a jour impossible : relancez ce fichier."; exit 1; }
  echo "Etape 2/4 : suppression des fichiers en trop (git clean)"
  git clean -fd
  echo "Etape 3/4 : seance $choix inscrite dans le fichier SEANCE"
  echo "$choix" > SEANCE
  echo "Etape 4/4 : recreation d'Odoo pour la seance $choix"
  docker compose down -v
  bash ./demarrer.sh
  exit $?
}
main "$@"
