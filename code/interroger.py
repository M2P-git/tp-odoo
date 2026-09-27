"""Execute un SELECT d'un fichier SQL sur la base pedagogique.

Usage : python code/interroger.py code/requete_s2.sql
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "atlas_micro.sqlite"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python code/interroger.py chemin/vers/requete.sql")
    if not DATABASE.exists():
        raise SystemExit("Base absente. Lancez d'abord : python code/initialiser.py")
    query = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    if "___" in query:
        raise SystemExit("Complétez d'abord les blancs ___ du fichier SQL.")
    if not query.lstrip().lstrip("- ").upper().startswith("SELECT") and "SELECT" not in query.upper():
        raise SystemExit("Ce programme d'exercice attend une requête SELECT.")
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.execute(query)
        print(" | ".join(column[0] for column in cursor.description))
        for row in cursor:
            print(" | ".join(str(value) for value in row))


if __name__ == "__main__":
    main()
