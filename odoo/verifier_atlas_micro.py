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
controle("Fournisseurs de P-R10", ", ".join(r10.seller_ids.mapped("partner_id.name")), "TechRoute, AltRoute")

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

print()
if all(resultats):
    print("Tout est pret : l'instance correspond au jeu initial Atlas Micro.")
else:
    print(f"{resultats.count(False)} ecart(s). Apres un TP, c'est normal ; avant le premier TP,")
    print("relancez reinitialiser.cmd (Windows) ou ./reinitialiser.sh (macOS/Linux).")
