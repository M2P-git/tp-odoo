from odoo import http
from odoo.http import request


class CatalogueBibliotheque(http.Controller):
    """Page publique demandée par Khadija : la liste des livres et leurs exemplaires disponibles."""

    # website=True : page « frontend » (langue, mise en page publique), même sans l'application Site Web
    @http.route("/bibliotheque", type="http", auth="public", website=True)
    def catalogue(self, genre=None, **kw):
        # Un visiteur n'a aucun droit sur les livres : sudo() lit les données pour lui (lecture seule).
        Livre = request.env["biblio.livre"].sudo()
        genres = dict(Livre._fields["genre"].selection)
        domaine = [("genre", "=", genre)] if genre in genres else []
        livres = Livre.search(domaine, order="name")
        return request.render("bibliotheque_campus.page_catalogue", {
            "livres": livres,
            "genres": genres,
            "genre": genre,
        })
