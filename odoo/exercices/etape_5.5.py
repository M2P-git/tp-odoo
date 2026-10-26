# -*- coding: utf-8 -*-
"""Exercice Point de vente « La journée campus » (étape 5.5).

Chargé par init.sh quand le fichier SEANCE vaut 5.5, après la séance 5 (préparation et
corrections disponibles) :
    odoo shell -d atlas_micro < etape_5.5.py
- une seconde caisse, « Stand Campus » (espèces, carte bancaire, compte client), avec les mêmes
  produits que le comptoir ; sa session n'est pas ouverte : les étudiants l'ouvrent eux-mêmes.
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[exercice 5.5] {message}", flush=True)


Config = env["pos.config"]
comptoir = Config.search([("name", "=", "Comptoir Atlas Micro")], limit=1)
journal, method_ids = Config._create_journal_and_payment_methods(
    cash_journal_vals={"name": "Caisse du stand", "show_on_dashboard": False})
methods = env["pos.payment.method"].browse(method_ids)
methods.filtered("is_cash_count").name = "Espèces"
stand = Config.create({
    "name": "Stand Campus", "journal_id": journal.id, "payment_method_ids": [(6, 0, method_ids)],
    "limit_categories": True, "iface_available_categ_ids": [(6, 0, comptoir.iface_available_categ_ids.ids)],
    "receipt_header": "Atlas Micro · Stand Campus",
})
log(f"Caisse {stand.name} : {', '.join(methods.mapped('name'))} ; session à ouvrir par les étudiants.")

env.cr.commit()
