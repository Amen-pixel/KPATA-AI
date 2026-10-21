"""Calcule les résultats de la vérification humaine (tâche D).

Lit les fichiers d'échantillon remplis par le relecteur et calcule, par langue :
le pourcentage de sens correct, le pourcentage d'informations critiques
correctes, et la note moyenne de naturel.

Usage, depuis la racine du dépôt :
    python scripts/resultats_verification.py
"""
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "docs" / "verification"

OUI = {"oui", "o", "yes", "y", "1", "true", "vrai"}
NON = {"non", "n", "no", "0", "false", "faux"}


def lire(langue):
    chemin = DOSSIER / f"echantillon_{langue}.csv"
    if not chemin.exists():
        return None, f"{chemin.name} absent"
    with open(chemin, encoding="utf-8") as f:
        return list(csv.DictReader(f)), None


def oui_non(valeur):
    """'oui' -> True, 'non' -> False, vide ou illisible -> None."""
    v = (valeur or "").strip().lower()
    if v in OUI:
        return True
    if v in NON:
        return False
    return None


def note(valeur):
    """La note de naturel, entre 1 et 5. None si vide ou hors bornes."""
    try:
        n = float((valeur or "").strip().replace(",", "."))
    except ValueError:
        return None
    return n if 1 <= n <= 5 else None


def analyser(lignes):
    """Calcule les trois mesures. Les cases vides ne comptent pas."""
    sens = [oui_non(l.get("sens_correct (oui/non)")) for l in lignes]
    infos = [oui_non(l.get("infos_critiques_correctes (oui/non)")) for l in lignes]
    naturels = [note(l.get("naturel (1-5)")) for l in lignes]

    sens = [v for v in sens if v is not None]
    infos = [v for v in infos if v is not None]
    naturels = [v for v in naturels if v is not None]

    return {
        "lignes": len(lignes),
        "remplies_sens": len(sens),
        "remplies_infos": len(infos),
        "remplies_naturel": len(naturels),
        "pct_sens": 100 * sum(sens) / len(sens) if sens else None,
        "pct_infos": 100 * sum(infos) / len(infos) if infos else None,
        "naturel_moyen": sum(naturels) / len(naturels) if naturels else None,
        # Les annonces dont les informations critiques sont fausses malgré nos
        # contrôles automatiques : ce sont les plus instructives.
        "echecs_critiques": [l["id"] for l in lignes
                             if oui_non(l.get("infos_critiques_correctes (oui/non)")) is False],
    }


def afficher(langue, r):
    def pct(v):
        return f"{v:.0f} %" if v is not None else "non rempli"

    print(f"=== {langue} ===")
    print(f"  {r['lignes']} annonces dans l'échantillon")
    print(f"  sens correct              : {pct(r['pct_sens'])}"
          f"   ({r['remplies_sens']}/{r['lignes']} remplies)")
    print(f"  infos critiques correctes : {pct(r['pct_infos'])}"
          f"   ({r['remplies_infos']}/{r['lignes']} remplies)")
    moyenne = (f"{r['naturel_moyen']:.1f}/5" if r["naturel_moyen"] is not None
               else "non rempli")
    print(f"  naturel moyen             : {moyenne}"
          f"   ({r['remplies_naturel']}/{r['lignes']} remplies)")
    if r["echecs_critiques"]:
        print(f"  ATTENTION — informations critiques fausses malgré les contrôles "
              f"automatiques : ids {r['echecs_critiques']}")
        print(f"              Ces annonces doivent être retirées du jeu de données, "
              f"et les règles de controle_traduction.py revues.")


def main():
    trouve = False
    for langue in ("yoruba", "hausa"):
        lignes, erreur = lire(langue)
        if erreur:
            print(f"=== {langue} ===\n  {erreur}\n")
            continue
        trouve = True
        afficher(langue, analyser(lignes))
        print()

    if not trouve:
        print("Aucun échantillon à analyser.")
        print("Lance d'abord scripts/echantillon_verification.py, puis fais "
              "remplir les fichiers par un relecteur.")
        return

    print("Rappel : ces mesures portent sur un échantillon de 20 annonces par "
          "langue. Elles donnent un ordre de grandeur, pas une mesure précise.")


if __name__ == "__main__":
    main()
