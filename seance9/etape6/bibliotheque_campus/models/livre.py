from odoo import api, fields, models


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
    nb_empruntes = fields.Integer("Empruntés", compute="_compute_disponibilite")
    nb_disponibles = fields.Integer("Disponibles", compute="_compute_disponibilite")

    @api.depends("nb_exemplaires", "emprunt_ids.state")
    def _compute_disponibilite(self):
        for livre in self:
            sortis = len(livre.emprunt_ids.filtered(lambda e: e.state == "emprunte"))
            livre.nb_empruntes = sortis
            livre.nb_disponibles = livre.nb_exemplaires - sortis
