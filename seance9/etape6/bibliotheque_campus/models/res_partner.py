from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    emprunt_ids = fields.One2many("biblio.emprunt", "adherent_id", string="Emprunts")
    nb_emprunts_en_cours = fields.Integer("Livres en main", compute="_compute_nb_emprunts_en_cours")

    @api.depends("emprunt_ids.state")
    def _compute_nb_emprunts_en_cours(self):
        for partenaire in self:
            partenaire.nb_emprunts_en_cours = len(
                partenaire.emprunt_ids.filtered(lambda e: e.state == "emprunte")
            )
