# -*- coding: utf-8 -*-
"""Préparation de la séance 4 : Atlas Micro assemble des postes de travail sur commande.

Chargé par init.sh quand la séance courante (fichier SEANCE) est supérieure ou égale à 4,
après le jeu de base et avant la correction de la séance 4. Le module Fabrication (mrp)
est installé par init.sh à partir de cette séance.
    odoo shell -d atlas_micro < preparation_s04.py
Volontairement absents : la nomenclature du poste et sa route de fabrication, que les
étudiants configurent pendant le TP. La variable « env » est fournie par « odoo shell ».
Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def ref(xmlid):
    return env.ref(xmlid, raise_if_not_found=False)


def log(message):
    print(f"[preparation s04] {message}", flush=True)


company = env.ref("base.main_company")
warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
buy = ref("purchase_stock.route_warehouse0_buy")
Partner = env["res.partner"]
techroute = Partner.search([("ref", "=", "F01")], limit=1)
dockpro = Partner.search([("ref", "=", "F02")], limit=1)
rapidis = Partner.search([("ref", "=", "F03")], limit=1)
meditech = Partner.search([("ref", "=", "C003")], limit=1)
sara = env["res.users"].search([("login", "=", "sara")], limit=1)
hamza = env["res.users"].search([("login", "=", "hamza")], limit=1)

# --- 1. Paramètres : numéros de série visibles, Hamza peut fabriquer -----------------
env["res.config.settings"].create({"group_stock_production_lot": True}).execute()
mrp_user = ref("mrp.group_mrp_user")
if mrp_user:
    hamza.write({"group_ids": [(4, mrp_user.id)]})
log("Numéros de série activés ; Hamza (magasinier) peut aussi assembler.")

# --- 2. Les composants, achetés et suivis en stock --------------------------------
categ_comp = env["product.category"].create({"name": "Composants"})
categ_poste = env["product.category"].create({"name": "Postes de travail"})
Template = env["product.template"]


def composant(name, code, cost, seller, delay, tracking):
    return Template.create({
        "name": name, "default_code": code,
        "type": "consu", "is_storable": True, "tracking": tracking,
        "list_price": 0.0, "standard_price": cost, "categ_id": categ_comp.id,
        "sale_ok": False, "route_ids": [(6, 0, [buy.id])],
        "seller_ids": [(0, 0, {"partner_id": seller.id, "price": cost, "delay": delay, "min_qty": 1})],
    }).product_variant_id


uc5 = composant("Unité centrale UC5", "P-UC5", 3100.0, techroute, 5, "serial")
e24 = composant("Écran 24 pouces E24", "P-E24", 1100.0, rapidis, 2, "serial")
k01 = composant("Kit clavier et souris K1", "P-K01", 150.0, dockpro, 3, "none")
log("Composants P-UC5 et P-E24 (suivis par numéro de série) et P-K01.")

# --- 3. Le produit fini, sans nomenclature ni route : c'est l'exercice ----------------
w1 = Template.create({
    "name": "Poste de travail Pro W1", "default_code": "P-W1",
    "type": "consu", "is_storable": True, "tracking": "serial",
    "list_price": 6900.0, "standard_price": 4350.0, "categ_id": categ_poste.id,
    "route_ids": [(6, 0, [])],
}).product_variant_id
log("Produit fini P-W1 (6 900 MAD), suivi par numéro de série, sans nomenclature.")

# --- 4. Stock initial : chaque unité suivie a son numéro de série ---------------------
Lot = env["stock.lot"]
Quant = env["stock.quant"].with_context(inventory_mode=True)
for product, prefix, qty in ((uc5, "UC5", 2), (e24, "E24", 6)):
    for i in range(1, qty + 1):
        lot = Lot.create({"name": f"{prefix}-{i:04d}", "product_id": product.id, "company_id": company.id})
        Quant.create({"product_id": product.id, "location_id": warehouse.lot_stock_id.id,
                      "lot_id": lot.id, "inventory_quantity": 1}).action_apply_inventory()
Quant.create({"product_id": k01.id, "location_id": warehouse.lot_stock_id.id,
              "inventory_quantity": 10}).action_apply_inventory()
log("Stock : 2 unités centrales (UC5-0001 et 0002), 6 écrans (E24-0001 à 0006), 10 kits.")

# --- 5. La demande : MediTech veut 4 postes (devis à confirmer pendant le TP) ----------
order = env["sale.order"].create({
    "name": "CO107", "partner_id": meditech.id, "user_id": sara.id,
    "date_order": "2026-10-05 10:00:00", "commitment_date": "2026-10-16 10:00:00",
    "order_line": [(0, 0, {"product_id": w1.id, "product_uom_qty": 4, "price_unit": 6900.0})],
})
log(f"Devis {order.name} : MediTech, 4 postes P-W1 ({order.state}).")

env.cr.commit()
