# -*- coding: utf-8 -*-
"""Contrôle continu 1, épreuve pratique (étape 5.9) : la semaine du Forum Smart City.

Chargé par init.sh quand le fichier SEANCE vaut 5.9, après la préparation de la séance 5 :
    odoo shell -d atlas_micro < etape_5.9.py
Le jeu est le même pour tous les étudiants : chacun obtient les mêmes résultats ; l'unicité des
copies vient du code (initiales) que l'étudiant porte sur tout ce qu'il crée pendant l'épreuve.
- la séance 5 est corrigée (caisse du comptoir fermée, comme au début de la séance 6) ;
- un nouveau fournisseur, NetSahara (Agadir) ;
- deux produits réseau : P-AP6 Borne Wi-Fi 6 AP6 (5 en stock, deux fournisseurs, règle 2 / 6)
  et P-S08 Switch 8 ports S8 (4 en stock, sans règle) ;
- CO108 : Nova Conseil, 2 bornes AP6, confirmée, livraison en attente ;
- un achat de 5 stations D2 chez DockPro, confirmé, non reçu (le réassort reste limité à l'AP6) ;
- une caisse « Stand Smart City » (espèces, carte bancaire, compte client), non ouverte.
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
root_env = env

# --- 0. La séance 5 corrigée : la caisse du comptoir est fermée -----------------------------
with open("/mnt/atlas/corrections/correction_s05.py", encoding="utf-8") as fichier:
    exec(compile(fichier.read(), "correction_s05.py", "exec"), {"env": root_env, "__name__": "correction_s05"})

admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def ref(xmlid):
    return env.ref(xmlid, raise_if_not_found=False)


def log(message):
    print(f"[controle 1] {message}", flush=True)


morocco = ref("base.ma")
warehouse = env["stock.warehouse"].search([], limit=1)
buy = ref("purchase_stock.route_warehouse0_buy")
Partner = env["res.partner"]
dockpro = Partner.search([("ref", "=", "F02")], limit=1)
rapidis = Partner.search([("ref", "=", "F03")], limit=1)
nova = Partner.search([("ref", "=", "C001")], limit=1)
sara = env["res.users"].search([("login", "=", "sara")], limit=1)
hamza = env["res.users"].search([("login", "=", "hamza")], limit=1)

# --- 1. Le fournisseur et les deux produits réseau ------------------------------------------
netsahara = Partner.create({
    "name": "NetSahara", "is_company": True, "ref": "F04", "city": "Agadir", "country_id": morocco.id,
    "email": "ventes@netsahara.example", "lang": "fr_FR", "supplier_rank": 1,
})
categ_reseau = env["product.category"].search([("name", "=", "Réseau")], limit=1)
Template = env["product.template"]
ap6 = Template.create({
    "name": "Borne Wi-Fi 6 AP6", "default_code": "P-AP6", "type": "consu", "is_storable": True,
    "list_price": 900.0, "standard_price": 560.0, "categ_id": categ_reseau.id,
    "route_ids": [(6, 0, [buy.id])],
    "seller_ids": [
        (0, 0, {"partner_id": netsahara.id, "price": 560.0, "delay": 7, "min_qty": 1, "sequence": 10}),
        (0, 0, {"partner_id": rapidis.id, "price": 640.0, "delay": 2, "min_qty": 1, "sequence": 20}),
    ],
}).product_variant_id
s08 = Template.create({
    "name": "Switch 8 ports S8", "default_code": "P-S08", "type": "consu", "is_storable": True,
    "list_price": 600.0, "standard_price": 380.0, "categ_id": categ_reseau.id,
    "route_ids": [(6, 0, [buy.id])],
    "seller_ids": [(0, 0, {"partner_id": dockpro.id, "price": 380.0, "delay": 3, "min_qty": 1})],
}).product_variant_id
Quant = env["stock.quant"].with_context(inventory_mode=True)
for product, qty in ((ap6, 5), (s08, 4)):
    Quant.create({"product_id": product.id, "location_id": warehouse.lot_stock_id.id,
                  "inventory_quantity": qty}).action_apply_inventory()
env["stock.warehouse.orderpoint"].create({
    "product_id": ap6.id, "warehouse_id": warehouse.id, "location_id": warehouse.lot_stock_id.id,
    "product_min_qty": 2, "product_max_qty": 6, "trigger": "manual", "route_id": buy.id,
})
log("Fournisseur F04 NetSahara ; P-AP6 (5 en stock, NetSahara 560 MAD 7 j, Rapidis 640 MAD 2 j, "
    "règle min 2 / max 6) ; P-S08 (4 en stock, DockPro 380 MAD 3 j).")

# --- 2. CO108 : les deux bornes de Nova Conseil, confirmées, pas encore livrées --------------
co108 = env["sale.order"].create({
    "name": "CO108", "partner_id": nova.id, "user_id": sara.id, "client_order_ref": "Salle de réunion de Yassine",
    "order_line": [(0, 0, {"product_id": ap6.id, "product_uom_qty": 2, "price_unit": 900.0})],
})
co108.action_confirm()
co108.picking_ids.write({"user_id": hamza.id})
log(f"CO108 Nova Conseil : 2 bornes AP6, confirmée ; livraison {co108.picking_ids[:1].name} "
    f"({co108.picking_ids[:1].state}).")

# Stations D2 : après la séance 5, le prévu vaut -1 (CO106, Bayt et deux stations vendues au
# comptoir). Leïla en a déjà commandé 5 chez DockPro : le réassort ne propose que la borne AP6.
leila = env["res.users"].search([("login", "=", "leila")], limit=1)
d02 = env["product.product"].search([("default_code", "=", "P-D02")], limit=1)
achat_d02 = env["purchase.order"].create({
    "partner_id": dockpro.id, "user_id": leila.id,
    "order_line": [(0, 0, {"product_id": d02.id, "product_qty": 5})],
})
achat_d02.button_confirm()
log(f"Achat {achat_d02.name} : 5 stations D2 chez DockPro, confirmé, réception en attente "
    f"(P-D02 prévu : {d02.virtual_available:.0f}).")

# --- 3. La caisse du stand, non ouverte ------------------------------------------------------
Config = env["pos.config"]
comptoir = Config.search([("name", "=", "Comptoir Atlas Micro")], limit=1)
journal, method_ids = Config._create_journal_and_payment_methods(
    cash_journal_vals={"name": "Caisse du stand Smart City", "show_on_dashboard": False})
methods = env["pos.payment.method"].browse(method_ids)
methods.filtered("is_cash_count").name = "Espèces"
methods.filtered(lambda m: m.journal_id.type == "bank").name = "Carte bancaire"
methods.filtered(lambda m: not m.journal_id).name = "Compte client"
stand = Config.create({
    "name": "Stand Smart City", "journal_id": journal.id, "payment_method_ids": [(6, 0, method_ids)],
    "limit_categories": True, "iface_available_categ_ids": [(6, 0, comptoir.iface_available_categ_ids.ids)],
    "receipt_header": "Atlas Micro - Forum Smart City",
})
log(f"Caisse {stand.name} : {', '.join(methods.mapped('name'))} ; session à ouvrir pendant l'épreuve.")

env["ir.config_parameter"].sudo().set_param("atlas_micro.examen", "CC1")
env.cr.commit()
