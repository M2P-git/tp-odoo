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

# --- Etape courante (fichier SEANCE) : « 3 » debut de la seance 3, « 3.3 » reprise a la mission 3 -----
try:
    with open("/mnt/seance", encoding="utf-8") as fichier:
        etape = fichier.read().strip().replace(",", ".") or "1"
    seance, _, mission = etape.partition(".")
    seance, mission = int(seance), int(mission) if mission else None
except (OSError, ValueError):
    etape, seance, mission = "1", 1, None
controle("Etape de la base", env["ir.config_parameter"].sudo().get_param("atlas_micro.seance"), etape)


def corrige(k, m):
    """La mission m de la seance k est-elle deja corrigee a cette etape ?"""
    return seance > k or (seance == k and mission is not None and m < mission)


# Seance 5 corrigee (caisse du comptoir fermee, ventes du comptoir faites) : a partir de la seance 6,
# et a l'etape 5.9 (Controle continu 1), dont le script d'exercice applique cette correction.
s5_corrigee = seance > 5 or etape == "5.9"

# Le routeur et CO104 : une fois la mission 2 de la seance 4 corrigee (16 routeurs achetes et
# recus, CO104 livree), d'ou d'autres valeurs initiales ; un routeur vendu au comptoir en seance 5.
r10 = env["product.product"].search([("default_code", "=", "P-R10")], limit=1)
controle("Produit P-R10", r10.name, "Routeur Pro R10")
r10_attendu = (11.0 if s5_corrigee else 12.0) if corrige(4, 2) else 6.0
controle("P-R10 en stock (en main)", r10.qty_available, r10_attendu)
controle("P-R10 previsionnel", r10.virtual_available, r10_attendu if corrige(4, 2) else -4.0)
controle("Fournisseurs de P-R10", ", ".join(r10.seller_ids.mapped("partner_id.name")), "TechRoute, Rapidis")

orders = {o.name: o for o in env["sale.order"].search([("name", "in", ["CO104", "CO105", "CO106"])])}
co104 = orders.get("CO104")
controle("CO104 etat", co104.state if co104 else None, "sale")
delivery = co104.picking_ids[:1] if co104 else env["stock.picking"]
controle("Livraison de CO104", delivery.state if delivery else None, "done" if corrige(4, 2) else "confirmed")
controle("CO105 etat", orders["CO105"].state if "CO105" in orders else None, "draft")

rule = env["stock.warehouse.orderpoint"].search([("product_id", "=", r10.id)], limit=1)
controle("Regle de reappro P-R10 (min/max)", (rule.product_min_qty, rule.product_max_qty) if rule else None, (3.0, 12.0))
controle("Reassort P-R10 : quantite a commander", rule.qty_to_order if rule else None, 0.0 if corrige(4, 2) else 16.0)

# --- Correction des seances precedentes ----------------------------------------------------

# Seance 3 : mission 1, Bayt Formation et Kasba Tours (+2) ; mission 3, Argan fusionne (-1)
leads = env["crm.lead"].with_context(active_test=False).search([("campaign_id", "!=", False)])
controle("Pistes et opportunites des campagnes", len(leads), 10 + 2 * corrige(3, 1) - corrige(3, 3))

if seance >= 3:  # correction de l'exercice de la seance 2 : la premiere affaire de Dar Services
    dar = env["res.partner"].search([("ref", "=", "C004")], limit=1)
    controle("Client C004", dar.name, "Dar Services")
    controle("Contact de Dar Services", ", ".join(dar.child_ids.mapped("name")), "Meryem")
    cable = env["product.product"].search([("default_code", "=", "P-C06")], limit=1)
    controle("Produit P-C06", cable.name, "Câble réseau Cat6 10 m")
    # Seance 5 corrigee : deux cables vendus au comptoir (Meryem, Dar Services).
    controle("P-C06 en stock (en main)", cable.qty_available, 18.0 if s5_corrigee else 20.0)
    controle("P-C06 previsionnel", cable.virtual_available,
             (3.0 if s5_corrigee else 5.0) if corrige(3, 1) else 15.0)
    commande = env["sale.order"].search([("partner_id", "=", dar.id)], limit=1)
    controle("Devis de Dar Services : etat", commande.state, "sale")
    livraison = commande.picking_ids[:1]
    controle("Livraison de Dar Services", livraison.state if livraison else None, "assigned")

if corrige(3, 1):  # correction de la mission 1 de la seance 3 : de la piste a la vente
    bayt = env["crm.lead"].search([("name", "=", "Salle de formation Bayt Formation")], limit=1)
    controle("Opportunite Bayt Formation", bayt.won_status if bayt else None, "won")
    vente = env["sale.order"].search([("opportunity_id", "=", bayt.id)], limit=1) if bayt else env["sale.order"]
    controle("Commande de Bayt Formation (MAD HT)", (vente.state, vente.amount_untaxed) if vente else None, ("sale", 2250.0))
    kasba = env["crm.lead"].with_context(active_test=False).search([("name", "=", "Wi-Fi des agences Kasba Tours")], limit=1)
    controle("Opportunite Kasba Tours", kasba.won_status if kasba else None, "lost")
    d02 = env["product.product"].search([("default_code", "=", "P-D02")], limit=1)
    # Seance 5 corrigee : deux stations vendues au comptoir (Samir) ; a l'etape 5.9, 5 stations
    # commandees chez DockPro et pas encore recues.
    controle("P-D02 previsionnel", d02.virtual_available,
             4.0 if etape == "5.9" else (-1.0 if s5_corrigee else 1.0))

if seance >= 3:  # mission 3 de la seance 3 : les deux pistes d'Argan Hotels, fusionnees une fois corrigee
    argan = env["crm.lead"].with_context(active_test=False).search([("email_normalized", "=", "imane@argan.example")])
    controle("Pistes Argan Hotels", len(argan), 1 if corrige(3, 3) else 2)

if seance >= 5:  # preparation de la seance 5 : le comptoir (Point de vente), TVA marocaine
    pos = env["ir.module.module"].search([("name", "=", "point_of_sale")], limit=1)
    controle("Application Point de vente", pos.state, "installed")
    controle("Plan comptable", company.chart_template, "ma")
    controle("TVA de vente par defaut", company.account_sale_tax_id.amount, 20.0)
    caisse = env["pos.config"].search([("name", "=", "Comptoir Atlas Micro")], limit=1)
    controle("Caisse Comptoir Atlas Micro", ", ".join(caisse.payment_method_ids.sorted("id").mapped("name")),
             "Espèces, Carte bancaire, Compte client")
    session = env["pos.session"].search([("config_id", "=", caisse.id)], order="id", limit=1)
    controle("Session du comptoir (etat, ouverte par, fonds)",
             (session.state, session.user_id.login, session.cash_register_balance_start) if session else None,
             ("closed" if s5_corrigee else "opened", "nadia", 500.0))
    if s5_corrigee:  # la journee du comptoir corrigee : sept tickets, dont un remboursement
        controle("Tickets du comptoir (DH TTC)", sorted(session.order_ids.mapped("amount_total")) if session else None,
                 [-60.0, 150.0, 270.0, 300.0, 348.0, 1080.0, 1440.0])
        stocks = (("P-S01", 28.0), ("P-U32", 39.0), ("P-H01", 11.0), ("P-A65", 14.0))
    else:
        controle("Tickets du matin (DH TTC)", sorted(session.order_ids.mapped("amount_total")) if session else None,
                 [150.0, 300.0])
        stocks = (("P-S01", 29.0), ("P-U32", 40.0), ("P-H01", 11.0), ("P-A65", 15.0))
    for code, stock in stocks:
        article = env["product.product"].search([("default_code", "=", code)], limit=1)
        controle(f"{code} en stock (en main)", article.qty_available, stock)

if etape == "5.5":  # exercice point de vente : la caisse du stand, pas encore ouverte
    stand = env["pos.config"].search([("name", "=", "Stand Campus")], limit=1)
    controle("Caisse Stand Campus (session ouverte ?)", (bool(stand), bool(stand.current_session_id)), (True, False))

if etape == "5.9":  # Controle continu 1 : le jeu de l'epreuve, encore intact
    controle("Jeu de l'epreuve", env["ir.config_parameter"].sudo().get_param("atlas_micro.examen"), "CC1")
    ap6 = env["product.product"].search([("default_code", "=", "P-AP6")], limit=1)
    s08 = env["product.product"].search([("default_code", "=", "P-S08")], limit=1)
    controle("P-AP6 (en stock, previsionnel)", (ap6.qty_available, ap6.virtual_available), (5.0, 3.0))
    controle("P-S08 (en stock, previsionnel)", (s08.qty_available, s08.virtual_available), (4.0, 4.0))
    regle = env["stock.warehouse.orderpoint"].search([("product_id", "=", ap6.id)], limit=1)
    controle("Regle de reappro P-AP6 (min/max)", (regle.product_min_qty, regle.product_max_qty) if regle else None,
             (2.0, 6.0))
    co108 = env["sale.order"].search([("name", "=", "CO108")], limit=1)
    controle("CO108 (etat, livraison)", (co108.state, co108.picking_ids[:1].state) if co108 else None, ("sale", "assigned"))
    controle("Commandes de vente (nombre)", env["sale.order"].search_count([]), 6)
    controle("Achats (nombre)", env["purchase.order"].search_count([]), 2)
    controle("Campagnes CRM", ", ".join(env["utm.campaign"].search([], order="id").mapped("title")), "Webinaire, Salon")
    stand = env["pos.config"].search([("name", "=", "Stand Smart City")], limit=1)
    controle("Caisse Stand Smart City (existe, session ouverte ?)", (bool(stand), bool(stand.current_session_id)),
             (True, False))
    controle("Utilisateur admin (pas encore renomme)", env.ref("base.user_admin").name, "Administrator")

if seance >= 6:  # preparation de la seance 6 : postes de travail assembles sur commande
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
