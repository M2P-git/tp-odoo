# -*- coding: utf-8 -*-
"""Charge le jeu de données fictif Atlas Micro dans la base Odoo du cours.

Exécuté automatiquement par init.sh au premier démarrage :
    odoo shell -d atlas_micro < charger_atlas_micro.py
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
import datetime as dt

SEED_KEY = "atlas_micro.seed_version"
SEED_VERSION = "2026.1"

root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def ref(xmlid):
    return env.ref(xmlid, raise_if_not_found=False)


def log(message):
    print(f"[atlas] {message}", flush=True)


# --- 1. Société, langue, paramètres -----------------------------------------
admin.sudo().write({"lang": "fr_FR", "tz": "Africa/Casablanca"})
mad = ref("base.MAD")
mad.sudo().active = True
morocco = ref("base.ma")
company = admin.company_id
company.sudo().write({
    "name": "Atlas Micro",
    "currency_id": mad.id,
    "country_id": morocco.id,
    "city": "Rabat",
    "email": "contact@atlas-micro.example",
})
env["product.pricelist"].with_context(active_test=False).search([]).write({"currency_id": mad.id})
env["res.config.settings"].create({"group_use_lead": True}).execute()
warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
warehouse.name = "Entrepôt Atlas Micro"
log("Société Atlas Micro (MAD), pistes CRM activées.")

# --- 2. Les acteurs internes (utilisateurs sans mot de passe) ---------------
def make_user(login, name, function, group_xmlids):
    groups = [ref("base.group_user").id] + [ref(x).id for x in group_xmlids if ref(x)]
    user = env["res.users"].with_context(no_reset_password=True).create({
        "name": name,
        "login": login,
        "email": f"{login}@atlas-micro.example",
        "group_ids": [(6, 0, groups)],
    })
    user.partner_id.write({"function": function, "lang": "fr_FR", "tz": "Africa/Casablanca"})
    return user

sara = make_user("sara", "Sara Alaoui", "Commerciale",
                 ["sales_team.group_sale_salesman_all_leads"])
hamza = make_user("hamza", "Hamza Tazi", "Magasinier", ["stock.group_stock_user"])
leila = make_user("leila", "Leïla Benjelloun", "Acheteuse", ["purchase.group_purchase_user"])
driss = make_user("driss", "Driss Amrani", "Comptable", ["account.group_account_invoice"])
log("Acteurs : Sara (commerciale), Hamza (magasinier), Leïla (acheteuse), Driss (comptable).")

# --- 3. Conditions de paiement, clients et fournisseurs ---------------------
net30 = ref("account.account_payment_term_30days")
immediat = ref("account.account_payment_term_immediate")
Partner = env["res.partner"]


def company_partner(name, code, city, email, **extra):
    vals = {"name": name, "is_company": True, "ref": code, "city": city,
            "country_id": morocco.id, "email": email, "lang": "fr_FR"}
    vals.update(extra)
    return Partner.create(vals)


nova = company_partner("Nova Conseil", "C001", "Rabat", "contact@nova.example",
                       customer_rank=1, property_payment_term_id=net30.id)
sigma = company_partner("École Sigma", "C002", "Salé", "contact@sigma.example",
                        customer_rank=1, property_payment_term_id=net30.id)
meditech = company_partner("MediTech", "C003", "Casablanca", "contact@meditech.example",
                           customer_rank=1, property_payment_term_id=immediat.id)
yassine = Partner.create({"name": "Yassine", "parent_id": nova.id, "email": "yassine@nova.example",
                          "function": "Responsable informatique", "lang": "fr_FR"})
Partner.create({"name": "Karim", "parent_id": sigma.id, "email": "karim@sigma.example",
                "function": "Responsable des achats", "lang": "fr_FR"})
Partner.create({"name": "Ghita", "parent_id": meditech.id, "email": "ghita@meditech.example",
                "function": "Directrice administrative", "lang": "fr_FR"})

techroute = company_partner("TechRoute", "F01", "Casablanca", "ventes@techroute.example", supplier_rank=1)
dockpro = company_partner("DockPro", "F02", "Tanger", "commandes@dockpro.example", supplier_rank=1)
rapidis = company_partner("Rapidis", "F03", "Rabat", "contact@rapidis.example", supplier_rank=1)
log("Clients C001 à C003 et fournisseurs F01 à F03 créés.")

# --- 4. Produits suivis en stock et fournisseurs ----------------------------
buy = ref("purchase_stock.route_warehouse0_buy")
categ_reseau = env["product.category"].create({"name": "Réseau"})
categ_acc = env["product.category"].create({"name": "Accessoires"})
Template = env["product.template"]
r10 = Template.create({
    "name": "Routeur Pro R10", "default_code": "P-R10",
    "type": "consu", "is_storable": True,
    "list_price": 1200.0, "standard_price": 780.0, "categ_id": categ_reseau.id,
    "route_ids": [(6, 0, [buy.id])],
    "seller_ids": [
        (0, 0, {"partner_id": techroute.id, "price": 780.0, "delay": 5, "min_qty": 1, "sequence": 10}),
        (0, 0, {"partner_id": rapidis.id, "price": 950.0, "delay": 2, "min_qty": 1, "sequence": 20}),
    ],
})
d02 = Template.create({
    "name": "Station d'accueil D2", "default_code": "P-D02",
    "type": "consu", "is_storable": True,
    "list_price": 450.0, "standard_price": 280.0, "categ_id": categ_acc.id,
    "route_ids": [(6, 0, [buy.id])],
    "seller_ids": [(0, 0, {"partner_id": dockpro.id, "price": 280.0, "delay": 3, "min_qty": 1})],
})
r10_p = r10.product_variant_id
d02_p = d02.product_variant_id

# Stock initial par ajustement d'inventaire validé (trace visible dans les mouvements).
Quant = env["stock.quant"].with_context(inventory_mode=True)
for product, qty in ((r10_p, 6), (d02_p, 8)):
    quant = Quant.create({"product_id": product.id, "location_id": warehouse.lot_stock_id.id,
                          "inventory_quantity": qty})
    quant.action_apply_inventory()
log("Produits P-R10 (6 en stock) et P-D02 (8 en stock) créés.")

# Règle de réapprovisionnement pédagogique : seuil 3, cible 12, déclenchement manuel.
env["stock.warehouse.orderpoint"].create({
    "product_id": r10_p.id, "warehouse_id": warehouse.id,
    "location_id": warehouse.lot_stock_id.id,
    "product_min_qty": 3, "product_max_qty": 12,
    "trigger": "manual", "route_id": buy.id,
})
log("Règle de réapprovisionnement P-R10 : min 3 / max 12 (manuelle).")

# --- 5. Ventes : CO104 confirmée, CO105 en devis, CO106 confirmée -----------
SaleOrder = env["sale.order"]


def sale(name, partner, product, qty, price, date_order, commitment, confirm, **extra):
    vals = {
        "name": name, "partner_id": partner.id, "user_id": sara.id,
        "date_order": date_order, "commitment_date": commitment,
        "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": qty, "price_unit": price})],
    }
    vals.update(extra)
    order = SaleOrder.create(vals)
    if confirm:
        order.action_confirm()
        order.date_order = date_order  # la confirmation remplace la date par « maintenant »
    return order


co104 = sale("CO104", nova, r10_p, 10, 1200.0, "2026-09-07 09:00:00", "2026-09-10 10:00:00", True,
             picking_policy="one", origin="Devis V-104", client_order_ref="Nouveau bureau de Yassine")
co105 = sale("CO105", sigma, r10_p, 2, 1200.0, "2026-09-08 11:00:00", "2026-09-15 10:00:00", False)
co106 = sale("CO106", meditech, d02_p, 3, 450.0, "2026-09-09 15:00:00", "2026-09-12 10:00:00", True)
for picking in (co104 | co106).picking_ids:
    picking.user_id = hamza
log("Commandes CO104 (confirmée, 10 routeurs), CO105 (devis), CO106 (confirmée).")

# --- 6. CRM : campagnes et pistes importées telles quelles (doublons inclus) --
Campaign = env["utm.campaign"]
campaigns = {"Webinaire": Campaign.create({"title": "Webinaire"}),
             "Salon": Campaign.create({"title": "Salon"})}
stages = {"qualifiee": ref("crm.stage_lead2"), "proposition": ref("crm.stage_lead3")}
lost_price = ref("crm.lost_reason_1")

# lead_id, date d'entrée, entreprise, contact, courriel, campagne, opportunité ?, état, montant
PROSPECTS = [
    ("L001", "2026-09-01", "Argan Hôtels", "Imane", "imane@argan.example", "Webinaire", 0, "nouveau", 0),
    ("L002", "2026-09-01", "Nova Conseil", "Yassine", "yassine@nova.example", "Webinaire", 1, "gagnee", 12000),
    ("L003", "2026-09-01", "NOVA CONSEIL", "Yassine", "YASSINE@NOVA.EXAMPLE", "Webinaire", 1, "gagnee", 12000),
    ("L004", "2026-09-02", "MediTech", "Ghita", "ghita@meditech.example", "Salon", 1, "perdue", 1350),
    ("L005", "2026-09-03", "Delta Labs", "Omar", "omar@delta.example", "Webinaire", 1, "proposition", 6000),
    ("L006", "2026-09-01", "Argan Hôtels", "Imane", "imane@argan.example", "Webinaire", 0, "nouveau", 0),
    ("L007", "2026-09-04", "Ecole Sigma", "Karim", "karim@sigma.example", "Salon", 1, "gagnee", 2400),
    ("L008", "2026-09-05", "Orbis Services", "Wafa", "wafa@orbis.example", "Webinaire", 1, "perdue", 4800),
    ("L009", "2026-09-06", "Zenith Industrie", "Amine", "amine@zenith.example", "Webinaire", 1, "gagnee", 3600),
    ("L010", "2026-09-07", "Riad Data", "Zineb", "zineb@riaddata.example", "Salon", 1, "qualifiee", 9000),
]
Lead = env["crm.lead"]
leads = {}
for lead_id, date_in, company_name, contact, email, campaign, is_opp, state, amount in PROSPECTS:
    name = f"{company_name} ({campaign})"
    if lead_id == "L002":
        name = "Équiper le nouveau bureau de Nova"
    vals = {
        "name": name, "partner_name": company_name, "contact_name": contact, "email_from": email,
        "campaign_id": campaigns[campaign].id, "type": "opportunity" if is_opp else "lead",
        "user_id": sara.id, "expected_revenue": amount,
        "description": f"Import de la campagne {campaign}, référence {lead_id}.",
    }
    if lead_id == "L002":
        vals["partner_id"] = yassine.id
    if state in stages:
        vals["stage_id"] = stages[state].id
    lead = Lead.create(vals)
    if state == "gagnee":
        lead.action_set_won()
    elif state == "perdue":
        lead.action_set_lost(lost_reason_id=lost_price.id if lost_price else False)
    leads[lead_id] = (lead, date_in, state)

# Dates d'entrée et de clôture conformes au scénario du livre.
for lead, date_in, state in leads.values():
    closed = "2026-09-15 17:00:00" if state in ("gagnee", "perdue") else None
    env.cr.execute(
        "UPDATE crm_lead SET create_date = %s, date_open = %s, date_closed = %s WHERE id = %s",
        (f"{date_in} 10:00:00", f"{date_in} 10:00:00", closed, lead.id),
    )

today = dt.date.today()
leads["L010"][0].activity_schedule("mail.mail_activity_data_call", date_deadline=today + dt.timedelta(days=2),
                                   summary="Appeler Zineb : budget et date de décision", user_id=sara.id)
leads["L005"][0].activity_schedule("mail.mail_activity_data_email", date_deadline=today + dt.timedelta(days=1),
                                   summary="Relancer Omar sur la proposition envoyée", user_id=sara.id)
log("CRM : 2 campagnes, 10 pistes (dont 2 doublons volontaires), 2 activités planifiées.")

# --- 7. Fin : marqueur de version et validation ------------------------------
env["ir.config_parameter"].sudo().set_param(SEED_KEY, SEED_VERSION)
env.cr.commit()
log(f"Jeu Atlas Micro chargé (version {SEED_VERSION}).")
