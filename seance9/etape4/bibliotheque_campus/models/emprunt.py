from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BiblioEmprunt(models.Model):
    _name = "biblio.emprunt"
    _description = "Emprunt"
    _order = "date_emprunt desc"
    _rec_name = "livre_id"

    livre_id = fields.Many2one("biblio.livre", string="Livre", required=True)
    adherent_id = fields.Many2one("res.partner", string="Adhérent", required=True)
    date_emprunt = fields.Date("Date d'emprunt", required=True, default=fields.Date.context_today)
    duree = fields.Integer("Durée (jours)", default=15)
    date_retour_prevue = fields.Date("Retour prévu", compute="_compute_date_retour_prevue", store=True)
    date_retour = fields.Date("Rendu le", readonly=True)
    retard = fields.Integer("Retard (jours)", compute="_compute_retard")
    state = fields.Selection(
        [("emprunte", "Emprunté"), ("rendu", "Rendu")],
        string="Statut",
        default="emprunte",
        required=True,
    )

    @api.depends("date_emprunt", "duree")
    def _compute_date_retour_prevue(self):
        for emprunt in self:
            if emprunt.date_emprunt:
                emprunt.date_retour_prevue = emprunt.date_emprunt + timedelta(days=emprunt.duree)
            else:
                emprunt.date_retour_prevue = False

    @api.depends("date_retour_prevue", "date_retour")
    def _compute_retard(self):
        aujourd_hui = fields.Date.context_today(self)
        for emprunt in self:
            fin = emprunt.date_retour or aujourd_hui
            if emprunt.date_retour_prevue and fin > emprunt.date_retour_prevue:
                emprunt.retard = (fin - emprunt.date_retour_prevue).days
            else:
                emprunt.retard = 0

    def action_rendre(self):
        for emprunt in self:
            emprunt.write({"state": "rendu", "date_retour": fields.Date.context_today(emprunt)})

    @api.constrains("livre_id", "state")
    def _check_exemplaire_disponible(self):
        for emprunt in self:
            if emprunt.state == "emprunte" and emprunt.livre_id.nb_disponibles < 0:
                raise ValidationError(
                    "Plus aucun exemplaire de « %s » n'est disponible." % emprunt.livre_id.name
                )

    @api.constrains("duree")
    def _check_duree(self):
        for emprunt in self:
            if emprunt.duree <= 0 or emprunt.duree > 60:
                raise ValidationError("La durée d'un emprunt va de 1 à 60 jours.")
