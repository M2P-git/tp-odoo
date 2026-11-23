{
    "name": "Bibliothèque du campus",
    "summary": "Livres, auteurs et emprunts de la bibliothèque",
    "version": "19.0.1.0.0",
    "category": "Services",
    "author": "CI3 BI",
    "license": "LGPL-3",
    "depends": ["contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/livre_views.xml",
        "views/auteur_views.xml",
        "views/emprunt_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
