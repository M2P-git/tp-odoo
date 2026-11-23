from odoo import fields, models


class BiblioEmprunt(models.Model):
    _name = "biblio.emprunt"
    _description = "Emprunt"
    _order = "date_emprunt desc"
    _rec_name = "livre_id"

    livre_id = fields.Many2one("biblio.livre", string="Livre", required=True)
    adherent_id = fields.Many2one("res.partner", string="Adhérent", required=True)
    date_emprunt = fields.Date("Date d'emprunt", required=True, default=fields.Date.context_today)
    duree = fields.Integer("Durée (jours)", default=15)
    date_retour = fields.Date("Rendu le")
    state = fields.Selection(
        [("emprunte", "Emprunté"), ("rendu", "Rendu")],
        string="Statut",
        default="emprunte",
        required=True,
    )
