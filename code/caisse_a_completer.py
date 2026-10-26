"""Semaine 5 : la journee du comptoir, recalculee a partir des tickets.

Completer les deux expressions TODO, puis lancer :
python code/caisse_a_completer.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "atlas_micro.sqlite"
TVA = 0.20            # taux unique des produits du comptoir
FONDS_DE_CAISSE = 500  # especes placees dans le tiroir a l'ouverture
ESPECES_COMPTEES = 2240
TOTAL_TPE = 1788       # ticket de fin de journee du terminal de paiement


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit("Base absente. Lancez d'abord : python code/initialiser.py")
    with sqlite3.connect(DATABASE) as connection:
        ca_ttc = connection.execute(
            "SELECT SUM(quantite * prix_ttc_mad) FROM lignes_tickets"
        ).fetchone()[0]
        nb_ventes, nb_retours = connection.execute(
            "SELECT SUM(ticket_origine IS NULL), SUM(ticket_origine IS NOT NULL) FROM tickets"
        ).fetchone()
        encaisse = dict(connection.execute(
            "SELECT moyen, SUM(montant_mad) FROM paiements_tickets GROUP BY moyen"
        ).fetchall())

    ca_ht = ca_ttc / (1 + TVA)
    tva = ca_ttc - ca_ht

    # TODO 1 : panier moyen = chiffre d'affaires TTC / nombre de tickets de vente
    panier_moyen = 0
    # TODO 2 : especes attendues = fonds de caisse + especes encaissees (remboursements compris)
    especes_attendues = 0

    print(f"Tickets : {nb_ventes} ventes, {nb_retours} remboursement(s)")
    print(f"Chiffre d'affaires : {ca_ttc:.0f} TTC = {ca_ht:.0f} HT + {tva:.0f} de TVA")
    print(f"Panier moyen : {panier_moyen:.0f} MAD TTC")
    print(f"Especes : attendues {especes_attendues:.0f}, comptees {ESPECES_COMPTEES}, "
          f"ecart {ESPECES_COMPTEES - especes_attendues:+.0f}")
    print(f"Carte : Odoo {encaisse.get('carte', 0):.0f}, terminal {TOTAL_TPE}, "
          f"ecart {TOTAL_TPE - encaisse.get('carte', 0):+.0f}")


if __name__ == "__main__":
    main()
