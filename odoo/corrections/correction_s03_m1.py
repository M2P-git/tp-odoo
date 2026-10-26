# -*- coding: utf-8 -*-
"""Correction de la séance 3, missions 1 et 2 : « Le pipeline de Sara ».

Chargé par init.sh à partir de l'étape 3.2 (fichier SEANCE : 3.2, 3.3, 4, 5...) ; la mission 2
(tableau croisé) ne modifie aucune donnée. La mission 3 est dans correction_s03_m3.py.
    odoo shell -d atlas_micro < correction_s03_m1.py
- Mission 1, niveau 1 : piste Bayt Formation (campagne Salon) convertie, qualifiée, devis S00002 confirmé, gagnée.
- Mission 1, niveau 2 : opportunité Kasba Tours (campagne Salon) perdue, motif « Trop cher ».
La variable « env » est fournie par « odoo shell ». Toutes les données sont fictives.
"""
import datetime as dt

root_env = env
admin = root_env.ref("base.user_admin")
ctx = dict(root_env.context, lang="fr_FR", tz="Africa/Casablanca", mail_create_nosubscribe=True)
env = root_env(user=admin, context=ctx)


def log(message):
    print(f"[correction s03] {message}", flush=True)


sara = env["res.users"].search([("login", "=", "sara")], limit=1)
salon = env["utm.campaign"].search([("title", "=", "Salon")], limit=1)
Lead = env["crm.lead"]

# --- Mission 1 : de la piste à la vente ------------------------------------------------------
lead = Lead.create({
    "name": "Salle de formation Bayt Formation", "type": "lead",
    "partner_name": "Bayt Formation", "contact_name": "Salma Berrada",
    "email_from": "salma@bayt-formation.example", "campaign_id": salon.id, "user_id": sara.id,
})
wizard = env["crm.lead2opportunity.partner"].with_context(
    active_model="crm.lead", active_id=lead.id, active_ids=lead.ids,
).create({"name": "convert", "action": "create", "user_id": sara.id})
wizard.action_apply()
lead.write({"expected_revenue": 2250.0, "stage_id": env.ref("crm.stage_lead2").id})
lead.activity_schedule("mail.mail_activity_data_call", date_deadline=dt.date.today() + dt.timedelta(days=2),
                       summary="Confirmer les quantités avec Salma", user_id=sara.id)
d02 = env["product.product"].search([("default_code", "=", "P-D02")], limit=1)
cable = env["product.product"].search([("default_code", "=", "P-C06")], limit=1)
order = env["sale.order"].create({
    "partner_id": lead.partner_id.id, "opportunity_id": lead.id, "user_id": sara.id,
    "campaign_id": salon.id,
    "order_line": [(0, 0, {"product_id": d02.id, "product_uom_qty": 4}),
                   (0, 0, {"product_id": cable.id, "product_uom_qty": 10})],
})
order.action_confirm()
lead.action_set_won()
log(f"Bayt Formation : opportunité gagnée, client {lead.partner_id.display_name}, commande {order.name} "
    f"({order.amount_untaxed:.0f} MAD HT).")

kasba = Lead.create({
    "name": "Wi-Fi des agences Kasba Tours", "type": "opportunity", "partner_name": "Kasba Tours",
    "contact_name": "Youssef", "email_from": "youssef@kasba-tours.example", "expected_revenue": 7200.0,
    "campaign_id": salon.id, "user_id": sara.id,
})
trop_cher = env.ref("crm.lost_reason_1", raise_if_not_found=False)
kasba.action_set_lost(lost_reason_id=trop_cher.id if trop_cher else False)
log("Kasba Tours : opportunité perdue, motif « Trop cher ».")

env.cr.commit()
