# -*- coding: utf-8 -*-
"""Correction de la séance 5 : « Samedi au comptoir » (Point de vente).
Chargé par init.sh à partir de la séance 6, après la préparation de la séance 5.
    odoo shell -d atlas_micro < correction_s05.py
- Mission 1 : Youssef, 2 clés USB et 1 souris (270 MAD), paie 300 en espèces, monnaie 30.
- Mission 2 : Meryem (Dar Services) chargeur et 2 câbles, carte, avec facture (348) ; Reda, un
  routeur par carte (1 440) ; Youssef rapporte une clé, remboursée en espèces (-60) ; Samir,
  2 stations d'accueil (1 080), paie 1 100 en espèces, monnaie 20.
- Mission 3 : le ticket du casque, payé en billets mais saisi en carte, est corrigé ; la caisse est
  fermée avec 2 240 MAD comptés et 1 788 MAD par carte (aucun écart).
La mission 4 (script) ne modifie aucune donnée. La variable « env » est fournie par « odoo shell ».
Toutes les données sont fictives.
"""
root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[correction s05] {message}", flush=True)


Product = env["product.product"]
souris, cle, casque, chargeur, cable, routeur, station = (
    Product.search([("default_code", "=", code)], limit=1)
    for code in ("P-S01", "P-U32", "P-H01", "P-A65", "P-C06", "P-R10", "P-D02"))
dar = env["res.partner"].search([("ref", "=", "C004")], limit=1)
session = env["pos.session"].search([("config_id.name", "=", "Comptoir Atlas Micro"), ("state", "=", "opened")], limit=1)
methods = session.config_id.payment_method_ids
especes = methods.filtered("is_cash_count")
carte = methods.filtered(lambda m: m.journal_id.type == "bank")
Order = env["pos.order"]


def ticket(lignes, paiements, client=None, facture=False, rembourse=None):
    """Un ticket encaissé comme à la caisse : lignes (produit, quantité), puis paiements
    (moyen, montant) ; un montant négatif en espèces est la monnaie rendue."""
    vals, total, taxe = [], 0.0, 0.0
    for product, qty in lignes:
        calcul = product.taxes_id.compute_all(product.lst_price, quantity=qty, product=product)
        ligne = {
            "product_id": product.id, "qty": qty, "price_unit": product.lst_price,
            "price_subtotal": calcul["total_excluded"], "price_subtotal_incl": calcul["total_included"],
            "tax_ids": [(6, 0, product.taxes_id.ids)], "full_product_name": product.display_name,
        }
        if rembourse:
            ligne["refunded_orderline_id"] = rembourse.lines.filtered(lambda l: l.product_id == product)[:1].id
        vals.append((0, 0, ligne))
        total += calcul["total_included"]
        taxe += calcul["total_included"] - calcul["total_excluded"]
    order = Order.create({
        "session_id": session.id, "user_id": admin.id, "lines": vals,
        "partner_id": client.id if client else False, "to_invoice": facture,
        "amount_tax": taxe, "amount_total": total, "amount_paid": 0.0, "amount_return": 0.0,
    })
    for methode, montant in paiements:
        order.add_payment({"pos_order_id": order.id, "amount": montant, "payment_method_id": methode.id,
                           "is_change": montant < 0 and total > 0})
    order.action_pos_order_paid()
    order._create_order_picking()
    order._compute_total_cost_in_real_time()
    if facture:
        order.action_pos_order_invoice()
    return order


# --- Mission 1 : Youssef ---------------------------------------------------------------------
youssef = ticket([(cle, 2), (souris, 1)], [(especes, 300.0), (especes, -30.0)])
log(f"Mission 1 : ticket {youssef.pos_reference}, {youssef.amount_total:.0f} MAD (300 reçus, monnaie 30).")

# --- Mission 2 : l'après-midi au comptoir -----------------------------------------------------
meryem = ticket([(chargeur, 1), (cable, 2)], [(carte, 348.0)], client=dar, facture=True)
reda = ticket([(routeur, 1)], [(carte, 1440.0)])
retour = ticket([(cle, -1)], [(especes, -60.0)], rembourse=youssef)
samir = ticket([(station, 2)], [(especes, 1100.0), (especes, -20.0)])
log(f"Mission 2 : Meryem {meryem.amount_total:.0f} (facture {meryem.account_move.name}), "
    f"Reda {reda.amount_total:.0f}, remboursement {retour.amount_total:.0f}, Samir {samir.amount_total:.0f}.")

# --- Mission 3 : corriger le ticket du casque, puis fermer la caisse --------------------------
casque_ticket = session.order_ids.filtered(lambda o: o.lines.product_id == casque)[:1]
casque_ticket.payment_ids.write({"payment_method_id": especes.id})
attendu = session.cash_register_balance_start + sum(
    session.order_ids.payment_ids.filtered(lambda p: p.payment_method_id == especes).mapped("amount"))
total_carte = sum(session.order_ids.payment_ids.filtered(lambda p: p.payment_method_id == carte).mapped("amount"))
session.post_closing_cash_details(2240.0)
session.update_closing_control_state_session("Ticket du casque corrigé : payé en espèces, saisi en carte.")
resultat = session.close_session_from_ui([(carte.id, 0.0)])
log(f"Mission 3 : ticket {casque_ticket.pos_reference} passé en espèces ; attendu {attendu:.0f}, "
    f"compté 2240, carte {total_carte:.0f} ; session {session.name} : {session.state} ({resultat}).")

env.cr.commit()
