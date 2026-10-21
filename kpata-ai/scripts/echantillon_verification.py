"""Tire au hasard un échantillon à faire relire par un locuteur (tâche D).

Objectif : qu'un relecteur puisse mesurer la qualité de la traduction
automatique **en une heure**, soit 20 annonces par langue.

La graine est fixe : le même tirage peut être refait à l'identique, ce qui
permet de comparer deux relecteurs sur le même échantillon.

Usage, depuis la racine du dépôt :
    python scripts/echantillon_verification.py
    python scripts/echantillon_verification.py --taille 10 --graine 7
"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
sys.path.insert(0, str(RACINE / "src"))

DOSSIER_BRIEFS = RACINE / "data" / "briefs"
DOSSIER_SORTIE = RACINE / "docs" / "verification"

GRAINE = 20261021          # date du tirage : facile à retrouver
TAILLE = 20                # 20 annonces par langue, environ une heure de travail

# Les quatre dernières colonnes sont vides : c'est le relecteur qui les remplit.
COLONNES = ["id", "texte_fr", "traduction",
            "sens_correct (oui/non)", "infos_critiques_correctes (oui/non)",
            "naturel (1-5)", "commentaire"]


def tirer(langue, taille=TAILLE, graine=GRAINE):
    """Tire `taille` annonces acceptées, au hasard mais de façon reproductible."""
    source = DOSSIER_BRIEFS / f"briefs_{langue}_auto.json"
    if not source.exists():
        print(f"  {source.name} absent : lance d'abord scripts/traduire_auto.py")
        return []

    annonces = json.loads(source.read_text(encoding="utf-8"))
    if not annonces:
        print(f"  aucune annonce acceptée en {langue}")
        return []

    # On trie par id avant de tirer : le tirage ne dépend pas de l'ordre du
    # fichier, donc il reste identique même si le fichier est régénéré.
    annonces = sorted(annonces, key=lambda a: a["id"])
    tireur = random.Random(f"{graine}-{langue}")
    retenues = tireur.sample(annonces, min(taille, len(annonces)))
    return sorted(retenues, key=lambda a: a["id"])


def exporter(langue, annonces):
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_SORTIE / f"echantillon_{langue}.csv"
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        redacteur = csv.DictWriter(f, fieldnames=COLONNES)
        redacteur.writeheader()
        for annonce in annonces:
            redacteur.writerow({
                "id": annonce["id"],
                "texte_fr": annonce["texte_source_fr"],
                "traduction": annonce["transcript"],
                "sens_correct (oui/non)": "",
                "infos_critiques_correctes (oui/non)": "",
                "naturel (1-5)": "",
                "commentaire": "",
            })
    return chemin


def main():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--taille", type=int, default=TAILLE)
    parseur.add_argument("--graine", type=int, default=GRAINE)
    args = parseur.parse_args()

    for langue in ("yoruba", "hausa"):
        print(f"=== {langue} ===")
        annonces = tirer(langue, args.taille, args.graine)
        if annonces:
            chemin = exporter(langue, annonces)
            print(f"  {len(annonces)} annonces -> {chemin}")
            print(f"  ids : {[a['id'] for a in annonces]}")

    print(f"\nGraine utilisée : {args.graine} (le tirage est reproductible)")
    print(f"Consignes pour le relecteur : "
          f"{(DOSSIER_SORTIE / 'consignes_relecteur.md').relative_to(RACINE)}")


if __name__ == "__main__":
    main()
