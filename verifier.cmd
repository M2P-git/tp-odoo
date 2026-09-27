@echo off
setlocal
cd /d "%~dp0"
echo Verification du jeu Atlas Micro dans Odoo (30 s environ)...
docker compose exec -T odoo odoo shell -d atlas_micro --db_host=db --db_user=odoo --db_password=odoo --no-http --log-level=error < odoo\verifier_atlas_micro.py > verification.log 2>&1
type verification.log
echo.
pause
