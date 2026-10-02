"""Cree une base SQLite de demonstration depuis les CSV fictifs du livre.

Usage (dans le dossier du depot tp-odoo) : python code/initialiser.py
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATABASE = DATA / "atlas_micro.sqlite"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE modalites_paiement (
    modalite_code TEXT PRIMARY KEY,
    libelle TEXT NOT NULL
);
CREATE TABLE fournisseurs (
    fournisseur_id TEXT PRIMARY KEY,
    nom TEXT NOT NULL,
    delai_jours INTEGER NOT NULL CHECK (delai_jours >= 0),
    prix_achat_mad INTEGER NOT NULL CHECK (prix_achat_mad >= 0)
);
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,
    nom TEXT NOT NULL,
    modalite_code TEXT NOT NULL REFERENCES modalites_paiement(modalite_code)
);
CREATE TABLE produits (
    produit_id TEXT PRIMARY KEY,
    libelle TEXT NOT NULL,
    prix_catalogue_mad INTEGER NOT NULL CHECK (prix_catalogue_mad >= 0),
    fournisseur_id TEXT NOT NULL REFERENCES fournisseurs(fournisseur_id)
);
CREATE TABLE commandes (
    commande_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(client_id),
    date_commande TEXT NOT NULL,
    etat TEXT NOT NULL CHECK (etat IN ('brouillon', 'confirmee')),
    modalite_code TEXT NOT NULL REFERENCES modalites_paiement(modalite_code)
);
CREATE TABLE lignes_commandes (
    commande_id TEXT NOT NULL REFERENCES commandes(commande_id),
    produit_id TEXT NOT NULL REFERENCES produits(produit_id),
    quantite INTEGER NOT NULL CHECK (quantite > 0),
    prix_unitaire_mad INTEGER NOT NULL CHECK (prix_unitaire_mad >= 0),
    PRIMARY KEY (commande_id, produit_id)
);
CREATE TABLE stock (
    produit_id TEXT PRIMARY KEY REFERENCES produits(produit_id),
    quantite_en_main INTEGER NOT NULL CHECK (quantite_en_main >= 0),
    entrees_attendues INTEGER NOT NULL CHECK (entrees_attendues >= 0),
    autres_sorties_prevues INTEGER NOT NULL CHECK (autres_sorties_prevues >= 0)
);
"""

TABLES = [
    "modalites_paiement",
    "fournisseurs",
    "clients",
    "produits",
    "commandes",
    "lignes_commandes",
    "stock",
]


def load_rows(name: str) -> list[dict[str, str]]:
    with (DATA / f"{name}.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def main() -> None:
    if DATABASE.exists():
        DATABASE.unlink()
    with sqlite3.connect(DATABASE) as connection:
        connection.executescript(SCHEMA)
        for table in TABLES:
            rows = load_rows(table)
            if not rows:
                continue
            columns = list(rows[0])
            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            connection.executemany(sql, [tuple(row[c] for c in columns) for row in rows])
        connection.commit()
    print(f"Base creee : {DATABASE}")
    print("3 clients, 2 produits, 3 commandes, 3 lignes, 2 lignes de stock.")


if __name__ == "__main__":
    main()
