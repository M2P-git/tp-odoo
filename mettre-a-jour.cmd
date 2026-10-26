@echo off
setlocal
chcp 65001 >nul
title TP Odoo : mise a jour vers une seance
cd /d "%~dp0"
rem Usage : mettre-a-jour.cmd        le numero de la seance est demande (liste affichee)
rem         mettre-a-jour.cmd 4      numero donne directement ; 3.3 = seance 3, reprise a la mission 3
set "CHOIX=%~1"

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

echo Recuperation des seances publiees ^(git fetch^)...
git fetch origin --tags
if errorlevel 1 (
  echo [ERREUR] Impossible de joindre GitHub : verifiez la connexion Internet.
  pause
  exit /b 1
)
set "DEFAUT="
for /f "usebackq delims=" %%s in (`git show origin/main:SEANCE`) do set "DEFAUT=%%s"

echo ============================================================
echo  TP Odoo : choisir la seance
echo ============================================================
echo  Numero   Ce que vous obtenez
git show origin/main:seances.txt | findstr /v /b /c:"#"
echo.
if not defined CHOIX set /p "CHOIX=Numero donne par l'enseignant (Entree = %DEFAUT%) : "
if not defined CHOIX set "CHOIX=%DEFAUT%"
set "CHOIX=%CHOIX:,=.%"
git show origin/main:seances.txt | findstr /b /l /c:"%CHOIX% " >nul
if errorlevel 1 (
  echo [ERREUR] Numero inconnu : %CHOIX%. Relancez et tapez un numero de la liste.
  pause
  exit /b 1
)

echo.
echo Seance choisie : %CHOIX%
echo ATTENTION :
echo   - vos modifications dans les fichiers de ce dossier seront EFFACEES ;
echo   - Odoo sera recree : vos saisies dans Odoo seront PERDUES.
echo Copiez ailleurs ce que vous voulez garder, puis confirmez.
choice /c ON /m "Continuer (O = oui, N = non) ?"
if errorlevel 2 exit /b 0

rem Tout le bloc ci-dessous est lu d'un coup par cmd : il reste valide meme si ce fichier est remplace par git reset.
(
  echo.
  echo Etape 1/4 : derniere version publiee ^(git reset --hard^)
  git reset --hard origin/main
  if errorlevel 1 (
    echo [ERREUR] Mise a jour impossible : relancez ce fichier.
    pause
    exit /b 1
  )
  echo Etape 2/4 : suppression des fichiers en trop ^(git clean^)
  git clean -fd
  echo Etape 3/4 : seance %CHOIX% inscrite dans le fichier SEANCE
  >SEANCE echo %CHOIX%
  echo Etape 4/4 : recreation d'Odoo pour la seance %CHOIX%
  docker compose down -v
  call "%~dp0demarrer.cmd"
  exit /b 0
)
