@echo off
cd /d "%~dp0"
echo Arret d'Odoo et de PostgreSQL (les donnees sont conservees)...
docker compose --profile sql stop
echo Termine. Relancez demarrer.cmd pour reprendre.
timeout /t 5 >nul
