# -*- coding: utf-8 -*-
"""Correction de l'exercice de la séance 2 : « La première affaire de Dar Services ».

Chargé par init.sh quand la séance courante (fichier SEANCE) est supérieure ou égale à 3 :
la séance 3 repart ainsi de l'état exact obtenu à la fin de la séance 2.
    odoo shell -d atlas_micro < correction_s02.py
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[correction s02] {message}", flush=True)


morocco = env.ref("base.ma")
net30 = env.ref("account.account_payment_term_30days")
warehouse = env["stock.warehouse"].search([], limit=1)
buy = env.ref("purchase_stock.route_warehouse0_buy")

# --- Étape 1 : le client (donnée maître) et son contact --------------------------------
Partner = env["res.partner"]
dar = Partner.create({
    "name": "Dar Services", "is_company": True, "ref": "C004", "city": "Marrakech",
    "country_id": morocco.id, "email": "contact@dar-services.example", "lang": "fr_FR",
    "customer_rank": 1, "property_payment_term_id": net30.id,
})
Partner.create({"name": "Meryem", "parent_id": dar.id, "email": "meryem@dar-services.example",
                "function": "Directrice des achats", "lang": "fr_FR"})
log("Client C004 Dar Services (30 jours) et son contact Meryem.")

# --- Étape 2 : le produit (donnée maître), suivi en stock ------------------------------
dockpro = Partner.search([("ref", "=", "F02")], limit=1)
categ_acc = env["product.category"].search([("name", "=", "Accessoires")], limit=1)
cable = env["product.template"].create({
    "name": "Câble réseau Cat6 10 m", "default_code": "P-C06",
    "type": "consu", "is_storable": True,
    "list_price": 45.0, "standard_price": 28.0, "categ_id": categ_acc.id,
    "route_ids": [(6, 0, [buy.id])],
    "seller_ids": [(0, 0, {"partner_id": dockpro.id, "price": 28.0, "delay": 3, "min_qty": 1})],
})
product = cable.product_variant_id
log("Produit P-C06 : prix 45 MAD, coût 28 MAD, fournisseur DockPro.")

# --- Étape 3 : le stock initial (ajustement d'inventaire validé) -----------------------
quant = env["stock.quant"].with_context(inventory_mode=True).create({
    "product_id": product.id, "location_id": warehouse.lot_stock_id.id, "inventory_quantity": 20,
})
quant.action_apply_inventory()
log("Stock initial de P-C06 : 20.")

# --- Étapes 4 et 5 : le devis, sa confirmation et la livraison créée -------------------
order = env["sale.order"].create({
    "partner_id": dar.id,
    "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": 5, "price_unit": 45.0})],
})
order.action_confirm()
log(f"Devis {order.name} confirmé ; livraison {order.picking_ids[:1].name} : {order.picking_ids[:1].state}.")

env.cr.commit()
