# -*- coding: utf-8 -*-
"""Préparation de la séance 5 : samedi au comptoir d'Atlas Micro (Point de vente).

Chargé par init.sh quand la séance courante (fichier SEANCE) est supérieure ou égale à 5,
après la correction de la séance 4. Le Point de vente (point_of_sale) et la localisation
marocaine (TVA à 20 %) sont installés par init.sh à partir de cette séance.
    odoo shell -d atlas_micro < preparation_s05.py
- la caisse « Comptoir Atlas Micro » : espèces, carte, compte client ;
- quatre accessoires vendus au comptoir, en plus du routeur, de la station et du câble ;
- la caisse du jour, ouverte ce matin par Nadia avec un fonds de 500 MAD, et ses deux tickets :
  une souris payée en espèces, puis un casque encaissé par carte alors que le client a payé
  en espèces (l'erreur que les étudiants retrouveront à la fermeture).
Les visuels des produits et le logo sont dans odoo/preparations/images/ (dessins du cours).
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
import base64

IMAGES = "/mnt/atlas/preparations/images"
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def ref(xmlid):
    return env.ref(xmlid, raise_if_not_found=False)


def log(message):
    print(f"[preparation s05] {message}", flush=True)


def image(nom):
    with open(f"{IMAGES}/{nom}.png", "rb") as fichier:
        return base64.b64encode(fichier.read())


company = env.ref("base.main_company")
company.logo = image("logo-atlas-micro")
warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
buy = ref("purchase_stock.route_warehouse0_buy")
Partner = env["res.partner"]
dockpro = Partner.search([("ref", "=", "F02")], limit=1)
rapidis = Partner.search([("ref", "=", "F03")], limit=1)

# --- 1. Nadia, vendeuse au comptoir ---------------------------------------------------------
groups = [ref("base.group_user").id, ref("point_of_sale.group_pos_user").id]
nadia = env["res.users"].with_context(no_reset_password=True).create({
    "name": "Nadia Chraibi", "login": "nadia", "email": "nadia@atlas-micro.example",
    "group_ids": [(6, 0, groups)],
})
nadia.partner_id.write({"function": "Vendeuse au comptoir", "lang": "fr_FR", "tz": "Africa/Casablanca"})
# L'administrateur et Driss voient les écritures comptables (lignes de débit et de crédit).
compta = ref("account.group_account_user")
(admin | env["res.users"].search([("login", "=", "driss")])).write({"group_ids": [(4, compta.id)]})
log("Actrice : Nadia (vendeuse au comptoir) ; écritures comptables visibles pour l'administrateur et Driss.")

# --- 2. Les produits du comptoir : prix hors taxes, affichés TTC (TVA 20 %) en caisse ---------
PosCateg = env["pos.category"]
reseau = PosCateg.create({"name": "Réseau", "sequence": 1, "color": 8})
accessoires = PosCateg.create({"name": "Accessoires", "sequence": 2, "color": 2})
categ_acc = env["product.category"].search([("name", "=", "Accessoires")], limit=1)
Template = env["product.template"]


def accessoire(name, code, price, cost, seller, delay, stock):
    product = Template.create({
        "name": name, "default_code": code, "type": "consu", "is_storable": True,
        "list_price": price, "standard_price": cost, "categ_id": categ_acc.id,
        "route_ids": [(6, 0, [buy.id])], "available_in_pos": True, "pos_categ_ids": [(6, 0, [accessoires.id])],
        "image_1920": image(code.lower()),
        "seller_ids": [(0, 0, {"partner_id": seller.id, "price": cost, "delay": delay, "min_qty": 1})],
    }).product_variant_id
    env["stock.quant"].with_context(inventory_mode=True).create({
        "product_id": product.id, "location_id": warehouse.lot_stock_id.id, "inventory_quantity": stock,
    }).action_apply_inventory()
    return product


souris = accessoire("Souris sans fil S1", "P-S01", 125.0, 70.0, dockpro, 3, 30)
cle = accessoire("Clé USB 32 Go", "P-U32", 50.0, 25.0, dockpro, 3, 40)
casque = accessoire("Casque audio H1", "P-H01", 250.0, 140.0, rapidis, 2, 12)
chargeur = accessoire("Chargeur USB-C 65 W", "P-A65", 200.0, 110.0, rapidis, 2, 15)
Product = env["product.product"]
for code, categ in (("P-R10", reseau), ("P-C06", reseau), ("P-D02", accessoires)):
    Product.search([("default_code", "=", code)], limit=1).product_tmpl_id.write({
        "available_in_pos": True, "pos_categ_ids": [(6, 0, [categ.id])], "image_1920": image(code.lower()),
    })
log("Comptoir : P-S01 souris (30), P-U32 clé USB (40), P-H01 casque (12), P-A65 chargeur (15), "
    "plus P-R10, P-C06 et P-D02 ; prix TTC en caisse.")

# --- 3. La caisse « Comptoir Atlas Micro » et ses moyens de paiement --------------------------
Config = env["pos.config"]
journal, method_ids = Config._create_journal_and_payment_methods(
    cash_journal_vals={"name": "Caisse du comptoir", "show_on_dashboard": False})
methods = env["pos.payment.method"].browse(method_ids)
especes = methods.filtered("is_cash_count")
carte = methods.filtered(lambda m: m.journal_id.type == "bank")
compte = methods.filtered(lambda m: not m.journal_id)
especes.name, carte.name, compte.name = "Espèces", "Carte bancaire", "Compte client"
config = Config.create({
    "name": "Comptoir Atlas Micro", "journal_id": journal.id, "payment_method_ids": [(6, 0, method_ids)],
    "limit_categories": True, "iface_available_categ_ids": [(6, 0, [reseau.id, accessoires.id])],
    "receipt_header": "Atlas Micro · Comptoir de Rabat",
})
log(f"Caisse {config.name} : {', '.join(methods.mapped('name'))}.")

# --- 4. Ce matin : Nadia ouvre la caisse (500 MAD) et encaisse deux tickets -------------------
session = env["pos.session"].create({"config_id": config.id, "user_id": nadia.id})
session.set_opening_control(500, "Fonds de caisse du samedi")
Order = env["pos.order"]


def ticket(lignes, methode):
    vals, total, taxe = [], 0.0, 0.0
    for product, qty in lignes:
        calcul = product.taxes_id.compute_all(product.lst_price, quantity=qty, product=product)
        vals.append((0, 0, {
            "product_id": product.id, "qty": qty, "price_unit": product.lst_price,
            "price_subtotal": calcul["total_excluded"], "price_subtotal_incl": calcul["total_included"],
            "tax_ids": [(6, 0, product.taxes_id.ids)], "full_product_name": product.display_name,
        }))
        total += calcul["total_included"]
        taxe += calcul["total_included"] - calcul["total_excluded"]
    order = Order.create({
        "session_id": session.id, "user_id": nadia.id, "lines": vals,
        "amount_tax": taxe, "amount_total": total, "amount_paid": 0.0, "amount_return": 0.0,
    })
    order.add_payment({"pos_order_id": order.id, "amount": total, "payment_method_id": methode.id})
    order.action_pos_order_paid()
    order._create_order_picking()
    order._compute_total_cost_in_real_time()
    return order


t1 = ticket([(souris, 1)], especes)
t2 = ticket([(casque, 1)], carte)   # le client a payé en espèces : erreur de Nadia
log(f"Session {session.name} ouverte par Nadia (fonds 500 MAD) ; tickets {t1.pos_reference} "
    f"({t1.amount_total:.0f} MAD, espèces) et {t2.pos_reference} ({t2.amount_total:.0f} MAD, carte).")

env.cr.commit()
