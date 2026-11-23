from odoo import fields, models


class BiblioAuteur(models.Model):
    _name = "biblio.auteur"
    _description = "Auteur"
    _order = "name"

    name = fields.Char("Nom", required=True)
    pays = fields.Char("Pays")
    livre_ids = fields.Many2many(
        "biblio.livre", "biblio_livre_auteur_rel", "auteur_id", "livre_id", string="Livres"
    )
