# -*- coding: utf-8 -*-
"""Vérifie que la base du cours contient le jeu Atlas Micro.

Lancé par verifier.cmd / verifier.sh :
    docker compose exec -T odoo odoo shell -d atlas_micro ... < odoo/verifier_atlas_micro.py
N'écrit rien dans la base. Un écart n'est pas forcément une erreur : il peut venir
d'une manipulation faite pendant un TP (réception validée, devis confirmé...).
"""

resultats = []


def controle(libelle, obtenu, attendu):
    ok = obtenu == attendu
    resultats.append(ok)
    marque = "OK " if ok else "ECART"
    detail = f"{obtenu}" if ok else f"{obtenu} (valeur initiale attendue : {attendu})"
    print(f"[{marque}] {libelle} : {detail}", flush=True)


company = env.ref("base.main_company")
controle("Societe", company.name, "Atlas Micro")
controle("Devise", company.currency_id.name, "MAD")
controle("Jeu de donnees", env["ir.config_parameter"].sudo().get_param("atlas_micro.seed_version"), "2026.1")

nova = env["res.partner"].search([("ref", "=", "C001")], limit=1)
controle("Client C001", nova.name, "Nova Conseil")
controle("Contact de Nova", ", ".join(nova.child_ids.mapped("name")), "Yassine")

r10 = env["product.product"].search([("default_code", "=", "P-R10")], limit=1)
controle("Produit P-R10", r10.name, "Routeur Pro R10")
controle("P-R10 en stock (en main)", r10.qty_available, 6.0)
controle("P-R10 previsionnel", r10.virtual_available, -4.0)
controle("Fournisseurs de P-R10", ", ".join(r10.seller_ids.mapped("partner_id.name")), "TechRoute, Rapidis")

orders = {o.name: o for o in env["sale.order"].search([("name", "in", ["CO104", "CO105", "CO106"])])}
co104 = orders.get("CO104")
controle("CO104 etat", co104.state if co104 else None, "sale")
delivery = co104.picking_ids[:1] if co104 else env["stock.picking"]
controle("Livraison de CO104", delivery.state if delivery else None, "confirmed")
controle("CO105 etat", orders["CO105"].state if "CO105" in orders else None, "draft")

rule = env["stock.warehouse.orderpoint"].search([("product_id", "=", r10.id)], limit=1)
controle("Regle de reappro P-R10 (min/max)", (rule.product_min_qty, rule.product_max_qty) if rule else None, (3.0, 12.0))
controle("Reassort P-R10 : quantite a commander", rule.qty_to_order if rule else None, 16.0)

leads = env["crm.lead"].with_context(active_test=False).search([("campaign_id", "!=", False)])
controle("Pistes CRM importees", len(leads), 10)

# --- Seance courante (fichier SEANCE) et correction des seances precedentes ----------------
try:
    with open("/mnt/seance", encoding="utf-8") as fichier:
        seance = int(fichier.read().strip() or 1)
except (OSError, ValueError):
    seance = 1
controle("Seance de la base", env["ir.config_parameter"].sudo().get_param("atlas_micro.seance"), str(seance))

if seance >= 3:  # correction de l'exercice de la seance 2 : la premiere affaire de Dar Services
    dar = env["res.partner"].search([("ref", "=", "C004")], limit=1)
    controle("Client C004", dar.name, "Dar Services")
    controle("Contact de Dar Services", ", ".join(dar.child_ids.mapped("name")), "Meryem")
    cable = env["product.product"].search([("default_code", "=", "P-C06")], limit=1)
    controle("Produit P-C06", cable.name, "Câble réseau Cat6 10 m")
    controle("P-C06 en stock (en main)", cable.qty_available, 20.0)
    controle("P-C06 previsionnel", cable.virtual_available, 15.0)
    commande = env["sale.order"].search([("partner_id", "=", dar.id)], limit=1)
    controle("Devis de Dar Services : etat", commande.state, "sale")
    livraison = commande.picking_ids[:1]
    controle("Livraison de Dar Services", livraison.state if livraison else None, "assigned")

if seance >= 4:  # preparation de la seance 4 : postes de travail assembles sur commande
    mrp = env["ir.module.module"].search([("name", "=", "mrp")], limit=1)
    controle("Application Fabrication", mrp.state, "installed")
    poste = env["product.product"].search([("default_code", "=", "P-W1")], limit=1)
    controle("Produit P-W1", poste.name, "Poste de travail Pro W1")
    controle("P-W1 suivi par numero de serie", poste.tracking, "serial")
    uc5 = env["product.product"].search([("default_code", "=", "P-UC5")], limit=1)
    controle("P-UC5 en stock (en main)", uc5.qty_available, 2.0)
    controle("Numeros de serie P-UC5", ", ".join(sorted(env["stock.lot"].search([("product_id", "=", uc5.id)]).mapped("name"))),
             "UC5-0001, UC5-0002")
    e24 = env["product.product"].search([("default_code", "=", "P-E24")], limit=1)
    controle("P-E24 en stock (en main)", e24.qty_available, 6.0)
    k01 = env["product.product"].search([("default_code", "=", "P-K01")], limit=1)
    controle("P-K01 en stock (en main)", k01.qty_available, 10.0)
    co107 = env["sale.order"].search([("name", "=", "CO107")], limit=1)
    controle("CO107 etat", co107.state if co107 else None, "draft")

print()
if all(resultats):
    print("Tout est pret : l'instance correspond au jeu initial Atlas Micro.")
else:
    print(f"{resultats.count(False)} ecart(s). Apres un TP, c'est normal ; avant le premier TP,")
    print("relancez reinitialiser.cmd (Windows) ou ./reinitialiser.sh (macOS/Linux).")
