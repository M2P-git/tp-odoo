#!/usr/bin/env bash
cd "$(dirname "$0")"
docker compose exec -T odoo odoo shell -d atlas_micro --db_host=db --db_user=odoo --db_password=odoo \
  --no-http --log-level=error < odoo/verifier_atlas_micro.py 2>&1 | tee verification.log
