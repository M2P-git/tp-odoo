# -*- coding: utf-8 -*-
"""Correction de la séance 3, mission 3 : « Nettoyer et recompter ».

Chargé par init.sh à partir de l'étape 3.4 (fichier SEANCE : 4, 5...), après correction_s03_m1.py.
    odoo shell -d atlas_micro < correction_s03_m3.py
- Mission 3, niveau 1 : les deux pistes d'Argan Hôtels (L001, L006) fusionnées.
  Les deux opportunités gagnées de Nova (L002, L003) restent : Odoo refuse de fusionner des affaires gagnées.
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[correction s03 m3] {message}", flush=True)


sara = env["res.users"].search([("login", "=", "sara")], limit=1)
argan = env["crm.lead"].search([("email_normalized", "=", "imane@argan.example"), ("type", "=", "lead")])
if len(argan) > 1:
    argan.merge_opportunity(user_id=sara.id)
log(f"Argan Hôtels : {len(argan)} pistes fusionnées en une.")

env.cr.commit()
