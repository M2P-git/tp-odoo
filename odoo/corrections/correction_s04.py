# -*- coding: utf-8 -*-
"""Correction des missions de la séance 4 : « Où sont mes routeurs ? ».

Chargé par init.sh quand la séance courante (fichier SEANCE) est supérieure ou égale à 5 :
la séance 5 repart ainsi de l'état obtenu à la fin de la séance 4.
    odoo shell -d atlas_micro < correction_s04.py
- Mission 2, niveau 1 : le réassort propose 16 routeurs ; demande de prix TechRoute confirmée.
- Mission 3, niveau 1 : réception des 16 routeurs validée, puis livraison des 10 routeurs de CO104.
Les niveaux 2 (demande de prix Rapidis annulée, réception partielle de stations D2) ne sont pas
rejoués : ils ne changent rien au stock dont la suite a besoin.
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[correction s04] {message}", flush=True)


def valider(picking):
    """Comme Hamza : toutes les quantités prévues sont comptées, puis « Valider »."""
    picking.action_assign()
    for move in picking.move_ids:
        move.quantity = move.product_uom_qty
        move.picked = True
    picking.button_validate()


r10 = env["product.product"].search([("default_code", "=", "P-R10")], limit=1)
techroute = env["res.partner"].search([("ref", "=", "F01")], limit=1)

# --- Mission 2 : le réassort, puis le bon de commande -----------------------------------------
rule = env["stock.warehouse.orderpoint"].search([("product_id", "=", r10.id)], limit=1)
rule.action_replenish()
achat = env["purchase.order"].search([("partner_id", "=", techroute.id), ("state", "=", "draft")],
                                     order="id desc", limit=1)
achat.button_confirm()
log(f"Réassort : {achat.name} chez TechRoute, {achat.order_line[:1].product_qty:.0f} routeurs "
    f"({achat.amount_untaxed:.0f} MAD HT), confirmé.")

# --- Mission 3 : la réception, puis la livraison de CO104 -------------------------------------
for reception in achat.picking_ids:
    valider(reception)
co104 = env["sale.order"].search([("name", "=", "CO104")], limit=1)
for livraison in co104.picking_ids.filtered(lambda p: p.state not in ("done", "cancel")):
    valider(livraison)
log(f"Réception validée ; livraison de CO104 : {co104.picking_ids[:1].state}. "
    f"Routeur : {r10.qty_available:.0f} disponibles, {r10.virtual_available:.0f} prévus.")

env.cr.commit()
