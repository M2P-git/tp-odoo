#!/bin/bash
# Prépare la base Odoo « atlas_micro » au premier démarrage (service « init »).
# La configuration dépend de l'étape indiquée dans le fichier SEANCE (monté sur /mnt/seance) :
# « N » (début de la séance N) ou « N.M » (séance N, reprise à la mission M), choisie par mettre-a-jour.
#   - le jeu de base Atlas Micro (charger_atlas_micro.py) est toujours chargé ;
#   - à partir de la séance 5, le Point de vente (point_of_sale) est installé en plus, avec la
#     localisation marocaine (plan comptable, TVA à 20 %) ;
#   - à partir de la séance 6, le module Fabrication (mrp) est installé en plus ;
#   - pour chaque séance k de 2 à N, on charge dans l'ordre la préparation de la séance k
#     (odoo/preparations/preparation_sNN.py, si elle existe : données nouvelles de la séance),
#     puis, si k < N, la correction de ses exercices (odoo/corrections/correction_sNN.py et
#     correction_sNN_mX.py, une par mission) : chaque séance repart de l'état corrigé de la précédente ;
#   - pour l'étape N.M, on charge aussi les corrections des missions X < M de la séance N.
# - base absente                        : création et chargement ;
# - base d'une autre étape / incomplète : suppression puis nouvelle création ;
# - base prête pour cette étape         : rien à faire.
set -euo pipefail

DB="atlas_micro"
ODOO_ARGS=(--db_host=db --db_port=5432 --db_user=odoo --db_password=odoo --log-level=warn)
ETAPE=$(tr -d ' \r\n' < /mnt/seance 2>/dev/null || true)
ETAPE=${ETAPE:-1}
ETAPE=${ETAPE/,/.}
if ! [[ "$ETAPE" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "[init] [ERREUR] Le fichier SEANCE contient « $ETAPE » : attendu un numero comme 3, 3.3 ou 5."
    exit 1
fi
SEANCE=${ETAPE%%.*}
MISSION=""
if [[ "$ETAPE" == *.* ]]; then MISSION=${ETAPE#*.}; fi
export ETAPE

etat=$(python3 - <<'PY'
import os, psycopg2
seance = os.environ["ETAPE"]
cn = psycopg2.connect(host="db", user="odoo", password="odoo", dbname="postgres")
cur = cn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'atlas_micro'")
if not cur.fetchone():
    print("absente")
else:
    try:
        db = psycopg2.connect(host="db", user="odoo", password="odoo", dbname="atlas_micro")
        c2 = db.cursor()
        c2.execute("SELECT value FROM ir_config_parameter WHERE key = 'atlas_micro.seance'")
        row = c2.fetchone()
        print("prete" if row and row[0] == seance else "incomplete")
        db.close()
    except Exception:
        print("incomplete")
cn.close()
PY
)

if [ "$etat" = "prete" ]; then
    echo "[init] La base atlas_micro est deja prete pour l'etape $ETAPE."
    exit 0
fi

if [ "$etat" = "incomplete" ]; then
    echo "[init] Base atlas_micro absente de cette seance ou incomplete : suppression avant une nouvelle creation."
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

MODULES="crm,sale_management,purchase,stock"
LIBELLE="CRM, Ventes, Achats et Inventaire"
if [ "$SEANCE" -ge 5 ]; then
    MODULES="$MODULES,point_of_sale,l10n_ma"
    LIBELLE="CRM, Ventes, Achats, Inventaire et Point de vente"
fi
if [ "$SEANCE" -ge 6 ]; then
    MODULES="$MODULES,mrp"
    LIBELLE="CRM, Ventes, Achats, Inventaire, Point de vente et Fabrication"
fi

if [ -n "$MISSION" ]; then
    echo "[init] Configuration de la seance $SEANCE, reprise a la mission $MISSION."
else
    echo "[init] Configuration de la seance $SEANCE."
fi
echo "[init] 1/3 Installation de $LIBELLE (interface en francais)."
echo "[init]     Premier lancement : compter 3 a 8 minutes selon le poste."
if [ "$SEANCE" -ge 5 ]; then
    # La societe est placee au Maroc avant l'installation de la comptabilite : Odoo charge alors
    # le plan comptable marocain (TVA a 20 %) au lieu du plan generique (taxe a 15 %).
    odoo "${ODOO_ARGS[@]}" -d "$DB" -i base --load-language=fr_FR --stop-after-init --no-http
    echo "env.company.country_id = env.ref('base.ma'); env.cr.commit()" \
        | odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http
fi
odoo "${ODOO_ARGS[@]}" -d "$DB" -i "$MODULES" \
     --load-language=fr_FR --stop-after-init --no-http

echo "[init] 2/3 Chargement du jeu de donnees fictif Atlas Micro."
odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http < /mnt/atlas/charger_atlas_micro.py

# Pour chaque seance k : sa preparation (donnees nouvelles), puis la correction de ses
# exercices si elle est deja passee (seance 3 : correction de la seance 2, etc.) ; pour la
# seance en cours, les missions deja faites en classe (etape N.M : missions avant M).
echo "[init] 3/3 Preparations et corrections des seances."
k=2
while [ "$k" -le "$SEANCE" ]; do
    prep=$(printf '/mnt/atlas/preparations/preparation_s%02d.py' "$k")
    if [ -f "$prep" ]; then
        echo "[init]     Preparation de la seance $k."
        odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http < "$prep"
    fi
    for script in $(printf '/mnt/atlas/corrections/correction_s%02d' "$k")*.py; do
        [ -f "$script" ] || continue
        nom=$(basename "$script" .py)
        mission=""
        if [[ "$nom" == *_m* ]]; then mission=${nom##*_m}; fi
        if [ "$k" -lt "$SEANCE" ]; then
            :
        elif [ "$k" -eq "$SEANCE" ] && [ -n "$MISSION" ] && [ -n "$mission" ] && [ "$mission" -lt "$MISSION" ]; then
            :
        else
            continue
        fi
        if [ -n "$mission" ]; then
            echo "[init]     Correction de la seance $k, mission $mission."
        else
            echo "[init]     Correction de la seance $k."
        fi
        odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http < "$script"
    done
    k=$((k + 1))
done

# Marqueur : la base correspond a cette etape.
echo "env['ir.config_parameter'].sudo().set_param('atlas_micro.seance', '$ETAPE'); env.cr.commit()" \
    | odoo shell "${ODOO_ARGS[@]}" -d "$DB" --no-http

echo "[init] Base atlas_micro prete (etape $ETAPE). Ouvrez http://localhost:8069 (admin / admin)."
