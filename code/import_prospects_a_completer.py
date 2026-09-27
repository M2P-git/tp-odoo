"""Semaine 3 : nettoyer un export CRM fictif et mesurer deux campagnes.

Completer les deux fonctions TODO, puis lancer depuis le dossier du depot :
python code/import_prospects_a_completer.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "prospects.csv"
NETTOYE = ROOT / "data" / "prospects_nettoyes.csv"
RAPPORT = ROOT / "data" / "rapport_prospects.txt"


def normaliser_email(valeur: str) -> str:
    # TODO 1 : apres strip(), convertir aussi les lettres en minuscules.
    return valeur.strip()


def est_gagnee(ligne: dict[str, str]) -> bool:
    # TODO 2 : renvoyer True si l'etat est "gagnee", False sinon.
    return False


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        lecteur = csv.DictReader(handle, delimiter=";")
        champs = list(lecteur.fieldnames or [])
        lignes = list(lecteur)

    vus: dict[str, str] = {}
    retenus: list[dict[str, str]] = []
    doublons: list[tuple[str, str]] = []
    for ligne in lignes:
        cle = normaliser_email(ligne["email"])
        if cle in vus:
            doublons.append((ligne["lead_id"], vus[cle]))
        else:
            vus[cle] = ligne["lead_id"]
            retenus.append(ligne)

    bilan: dict[str, dict[str, int]] = defaultdict(
        lambda: {"contacts": 0, "opportunites": 0, "gagnees": 0}
    )
    for ligne in retenus:
        stats = bilan[ligne["campagne"]]
        stats["contacts"] += 1
        stats["opportunites"] += int(ligne["est_opportunite"] == "1")
        stats["gagnees"] += int(est_gagnee(ligne))

    with NETTOYE.open("w", encoding="utf-8", newline="") as handle:
        ecrivain = csv.DictWriter(handle, fieldnames=champs, delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(retenus)

    lignes_rapport = [
        f"Lignes lues : {len(lignes)}",
        f"Contacts retenus : {len(retenus)}",
        "Doublons (retire -> conserve) : "
        + (", ".join(f"{a} -> {b}" for a, b in doublons) or "aucun"),
    ]
    for campagne, stats in sorted(bilan.items()):
        taux = 100 * stats["gagnees"] / stats["contacts"]
        lignes_rapport.append(
            f"{campagne} : {stats['contacts']} contacts, "
            f"{stats['opportunites']} opportunites, "
            f"{stats['gagnees']} gagnees, "
            f"taux piste -> vente gagnee {taux:.1f} %"
        )
    RAPPORT.write_text("\n".join(lignes_rapport) + "\n", encoding="utf-8")
    print("\n".join(lignes_rapport))
    print(f"Fichiers crees : {NETTOYE.name}, {RAPPORT.name}")


if __name__ == "__main__":
    main()
