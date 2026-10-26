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
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    heure TEXT NOT NULL,
    vendeuse TEXT NOT NULL,
    client TEXT,
    ticket_origine TEXT REFERENCES tickets(ticket_id)
);
CREATE TABLE lignes_tickets (
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    produit_id TEXT NOT NULL,
    libelle TEXT NOT NULL,
    quantite INTEGER NOT NULL CHECK (quantite <> 0),
    prix_ttc_mad INTEGER NOT NULL CHECK (prix_ttc_mad >= 0),
    cout_unitaire_mad INTEGER NOT NULL CHECK (cout_unitaire_mad >= 0),
    PRIMARY KEY (ticket_id, produit_id)
);
CREATE TABLE paiements_tickets (
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    moyen TEXT NOT NULL CHECK (moyen IN ('especes', 'carte', 'compte_client')),
    montant_mad INTEGER NOT NULL
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
    "tickets",
    "lignes_tickets",
    "paiements_tickets",
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
            # Une case vide du CSV devient NULL (client anonyme, ticket sans origine).
            connection.executemany(sql, [tuple(row[c] or None for c in columns) for row in rows])
        connection.commit()
    print(f"Base creee : {DATABASE}")
    print("3 clients, 2 produits, 3 commandes, 3 lignes, 2 lignes de stock.")
    print("Comptoir (seance 5) : 7 tickets, 9 lignes, 7 paiements.")


if __name__ == "__main__":
    main()
