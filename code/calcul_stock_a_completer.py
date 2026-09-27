"""Semaine 4 : calcul pedagogique du stock du routeur P-R10.

Completer les deux expressions TODO, puis lancer :
python code/calcul_stock_a_completer.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "atlas_micro.sqlite"
PRODUIT = "P-R10"
SEUIL = 3
CIBLE = 12


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit("Base absente. Lancez d'abord : python code/initialiser.py")
    with sqlite3.connect(DATABASE) as connection:
        stock = connection.execute(
            "SELECT quantite_en_main, entrees_attendues, autres_sorties_prevues "
            "FROM stock WHERE produit_id = ?",
            (PRODUIT,),
        ).fetchone()
        demande_confirmee = connection.execute(
            "SELECT COALESCE(SUM(lc.quantite), 0) "
            "FROM lignes_commandes AS lc "
            "JOIN commandes AS co ON co.commande_id = lc.commande_id "
            "WHERE lc.produit_id = ? AND co.etat = 'confirmee'",
            (PRODUIT,),
        ).fetchone()[0]
        demande_co104 = connection.execute(
            "SELECT quantite FROM lignes_commandes "
            "WHERE commande_id = 'CO104' AND produit_id = ?",
            (PRODUIT,),
        ).fetchone()[0]

    en_main, entrees, autres_sorties_prevues = map(int, stock)
    demande_confirmee = int(demande_confirmee)
    manque_co104 = max(0, demande_co104 - (en_main - autres_sorties_prevues))

    # TODO 1 : en_main + entrees - autres_sorties_prevues - demande_confirmee
    solde_previsionnel = 0
    # TODO 2 : si solde <= SEUIL, atteindre CIBLE ; sinon proposer 0.
    quantite_proposee = 0

    print(f"Produit : {PRODUIT}")
    print(f"En main : {en_main}")
    print(f"Demande confirmee : {demande_confirmee}")
    print(f"Manque pour CO104 : {manque_co104}")
    print(f"Solde previsionnel : {solde_previsionnel}")
    print(f"Proposition vers cible {CIBLE} : {quantite_proposee}")


if __name__ == "__main__":
    main()
