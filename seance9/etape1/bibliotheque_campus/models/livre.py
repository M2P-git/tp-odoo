from odoo import fields, models


class BiblioLivre(models.Model):
    _name = "biblio.livre"
    _description = "Livre"
    _order = "name"

    name = fields.Char("Titre", required=True)
    isbn = fields.Char("ISBN")
    annee = fields.Integer("Année de parution")
    nb_exemplaires = fields.Integer("Exemplaires", default=1)
