@echo off
setlocal
cd /d "%~dp0"
echo ATTENTION : toutes les modifications faites dans Odoo seront effacees.
echo La base atlas_micro sera recreee avec le jeu initial Atlas Micro.
choice /c ON /m "Continuer (O = oui, N = non) ?"
if errorlevel 2 exit /b 0
docker compose down -v
call "%~dp0demarrer.cmd"
