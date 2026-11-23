from odoo import fields, models


class BiblioLivre(models.Model):
    _name = "biblio.livre"
    _description = "Livre"
    _order = "name"

    name = fields.Char("Titre", required=True)
    isbn = fields.Char("ISBN")
    annee = fields.Integer("Année de parution")
    genre = fields.Selection(
        [
            ("roman", "Roman"),
            ("bd", "Bande dessinée"),
            ("informatique", "Informatique"),
            ("gestion", "Gestion"),
        ],
        string="Genre",
    )
    resume = fields.Text("Résumé")
    nb_exemplaires = fields.Integer("Exemplaires", default=1)
    auteur_ids = fields.Many2many(
        "biblio.auteur", "biblio_livre_auteur_rel", "livre_id", "auteur_id", string="Auteurs"
    )
    emprunt_ids = fields.One2many("biblio.emprunt", "livre_id", string="Emprunts")
