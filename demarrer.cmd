@echo off
setlocal
title ERP-CRM : demarrage de l'environnement Odoo
cd /d "%~dp0"
echo ============================================================
echo  Environnement de TP ERP ^& CRM : Odoo 19 + jeu Atlas Micro
echo ============================================================
docker info >nul 2>&1
if errorlevel 1 (
  echo [ERREUR] Docker ne repond pas.
  echo Lancez Docker Desktop, attendez "Engine running", puis relancez ce fichier.
  pause
  exit /b 1
)
echo.
echo Etape 1/3 : images Docker (environ 1 Go a telecharger la premiere fois)
docker compose pull
if errorlevel 1 echo [INFO] Telechargement impossible : utilisation des images deja presentes.
echo.
echo Etape 2/3 : preparation de la base atlas_micro (premiere fois : 3 a 8 min)
docker compose up -d
if errorlevel 1 goto echec
echo.
echo Etape 3/3 : attente du serveur Odoo
set /a essais=0
:attente
curl -s -o nul -m 3 http://localhost:8069/web/login
if not errorlevel 1 goto pret
set /a essais+=1
if %essais% geq 60 goto echec
timeout /t 3 >nul
goto attente

:pret
docker compose logs --no-color init > demarrage.log 2>&1
echo.
echo [OK] Odoo est pret : http://localhost:8069
echo      Identifiant : admin     Mot de passe : admin
start "" http://localhost:8069
timeout /t 10 >nul
exit /b 0

:echec
docker compose logs --no-color init > demarrage.log 2>&1
docker compose ps -a >> demarrage.log 2>&1
echo.
echo [ERREUR] Le demarrage n'a pas abouti. Montrez le fichier demarrage.log.
pause
exit /b 1
