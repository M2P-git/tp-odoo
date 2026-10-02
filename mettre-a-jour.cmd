@echo off
setlocal
chcp 65001 >nul
title TP Odoo : mise a jour vers la version de la seance
cd /d "%~dp0"
rem Usage : mettre-a-jour.cmd            (derniere version publiee, branche main)
rem         mettre-a-jour.cmd seance-02  (version figee d'une seance precise)
set "CIBLE=%~1"
if not defined CIBLE set "CIBLE=origin/main"

git --version >nul 2>&1
if errorlevel 1 (
  echo [ERREUR] Git n'est pas installe sur ce poste.
  echo Installez-le : winget install --id Git.Git -e   ^(ou https://git-scm.com/download/win^)
  echo Puis fermez et rouvrez ce fichier. Sans Git : telechargez le ZIP du depot et remplacez ce dossier.
  pause
  exit /b 1
)
if not exist ".git" (
  echo [ERREUR] Ce dossier n'a pas ete obtenu avec "git clone" : il n'y a pas d'historique Git.
  echo Utilisez : git clone https://github.com/M2P-git/tp-odoo.git
  pause
  exit /b 1
)

echo ============================================================
echo  TP Odoo : retour exact a la version de la seance (%CIBLE%)
echo ============================================================
echo ATTENTION :
echo   - vos modifications dans les fichiers de ce dossier seront EFFACEES ;
echo   - Odoo sera recree : vos saisies dans Odoo seront PERDUES.
echo Copiez ailleurs ce que vous voulez garder, puis confirmez.
choice /c ON /m "Continuer (O = oui, N = non) ?"
if errorlevel 2 exit /b 0

rem Tout le bloc ci-dessous est lu d'un coup par cmd : il reste valide meme si ce fichier est remplace par git reset.
(
  echo.
  echo Etape 1/4 : recuperation des nouveautes ^(git fetch^)
  git fetch origin --tags
  if errorlevel 1 (
    echo [ERREUR] Impossible de joindre GitHub : verifiez la connexion Internet.
    pause
    exit /b 1
  )
  echo Etape 2/4 : retour a la version de la seance ^(git reset --hard^)
  git reset --hard %CIBLE%
  if errorlevel 1 (
    echo [ERREUR] Version introuvable : %CIBLE%
    pause
    exit /b 1
  )
  echo Etape 3/4 : suppression des fichiers en trop ^(git clean^)
  git clean -fd
  echo Etape 4/4 : recreation d'Odoo avec la configuration de la seance
  docker compose down -v
  call "%~dp0demarrer.cmd"
  exit /b 0
)
