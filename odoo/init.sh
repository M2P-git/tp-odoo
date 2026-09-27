#!/bin/bash
# Prépare la base Odoo « atlas_micro » au premier démarrage (service « init »).
# - base absente    : création, installation des applications, chargement du jeu Atlas Micro ;
# - base incomplète : suppression puis nouvelle création ;
# - base prête      : rien à faire.
set -euo pipefail

DB="atlas_micro"
ODOO_ARGS=(--db_host=db --db_port=5432 --db_user=odoo --db_password=odoo --log-level=warn)

etat=$(python3 - <<'PY'
import psycopg2
cn = psycopg2.connect(host="db", user="odoo", password="odoo", dbname="postgres")
cur = cn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'atlas_micro'")
if not cur.fetchone():
    print("absente")
else:
    try:
        db = psycopg2.connect(host="db", user="odoo", password="odoo", dbname="atlas_micro")
        c2 = db.cursor()
        c2.execute("SELECT value FROM ir_config_parameter WHERE key = 'atlas_micro.seed_version'")
        print("prete" if c2.fetchone() else "incomplete")
        db.close()
    except Exception:
        print("incomplete")
cn.close()
PY
)

if [ "$etat" = "prete" ]; then
    echo "[init] La base atlas_micro est deja prete."
    exit 0
fi

if [ "$etat" = "incomplete" ]; then
    echo "[init] Base atlas_micro incomplete : suppression avant une nouvelle creation."
    python3 - <<'PY'
import psycopg2
cn = psycopg2.connect(host="db", user="odoo", password="odoo", dbname="postgres")
cn.autocommit = True
cur = cn.cursor()
cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'atlas_micro'")
cur.execute('DROP DATABASE IF EXISTS "atlas_micro"')
cn.close()
PY
    rm -rf /var/lib/odoo/filestore/atlas_micro
fi

echo "[init] 1/2 Installation de CRM, Ventes, Achats et Inventaire (interface en francais)."
echo "[init]     Premier lancement : compter 3 a 8 minutes selon le poste."
odoo "${ODOO_ARGS[@]}" -d "$DB" -i crm,sale_management,purchase,stock \
     --load-language=fr_FR --stop-after-init --no-http

echo "[init] 2/2 Chargement du jeu de donnees fictif Atlas Micro."
odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http < /mnt/atlas/charger_atlas_micro.py

echo "[init] Base atlas_micro prete. Ouvrez http://localhost:8069 (admin / admin)."
