"""Traduit les annonces en Yorùbá et en Hausa, sous contrôle de fidélité.

Modèle : NLLB-200 distillé 600M (Meta), licence CC-BY-NC 4.0 — usage NON
commercial. Tourne sur processeur, sans carte graphique.

Principe (D-010) : on traduit le français vers la langue cible, on retraduit
vers le français, puis on vérifie que les informations critiques ont survécu au
double passage. Une annonce qui échoue est **rejetée**, jamais corrigée à la
main : la règle d'or du cahier des charges (§7.2) interdit qu'un prix ou un
numéro faux arrive sur une affiche.

Usage, depuis la racine du dépôt :
    pip install -r requirements-phase1.txt
    python scripts/traduire_auto.py                # les deux langues
    python scripts/traduire_auto.py --langue hausa  # une seule
    python scripts/traduire_auto.py --limite 5      # essai rapide

Le modèle fait environ 2,5 Go : le premier lancement le télécharge.
"""
import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
sys.path.insert(0, str(RACINE / "src"))

from kpata.controle_traduction import controler, resumer  # noqa: E402

MODELE = "facebook/nllb-200-distilled-600M"
MODELE_VERSION = f"{MODELE} (CC-BY-NC-4.0)"

# Codes de langue NLLB (norme FLORES-200).
CODES = {"francais": "fra_Latn", "yoruba": "yor_Latn", "hausa": "hau_Latn"}

DOSSIER = RACINE / "data" / "briefs"
FICHIER_REJETS = DOSSIER / "rejets_traduction.json"


class Traducteur:
    """Enveloppe autour de NLLB. Le modèle est chargé une seule fois."""

    def __init__(self, nom=MODELE):
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        print(f"Chargement de {nom} (premier lancement : téléchargement ~2,5 Go)...")
        self.tokenizer = AutoTokenizer.from_pretrained(nom)
        self.modele = AutoModelForSeq2SeqLM.from_pretrained(nom)
        self.modele.eval()
        print("Modèle prêt.")

    def traduire(self, texte, depuis, vers):
        """Traduit un texte. `depuis` et `vers` sont des codes FLORES."""
        import torch
        self.tokenizer.src_lang = depuis
        entrees = self.tokenizer(texte, return_tensors="pt", truncation=True,
                                 max_length=256)
        # Le code de la langue cible force la sortie dans la bonne langue.
        cible = self.tokenizer.convert_tokens_to_ids(vers)
        with torch.no_grad():
            sortie = self.modele.generate(
                **entrees,
                forced_bos_token_id=cible,
                max_new_tokens=256,
                num_beams=4,            # un peu plus lent, nettement plus fidèle
                do_sample=False,        # pas d'aléatoire : résultat reproductible
            )
        return self.tokenizer.batch_decode(sortie, skip_special_tokens=True)[0].strip()


def traiter_langue(langue, traducteur, limite=None):
    """Traduit un fichier d'annonces et sépare les acceptées des rejetées."""
    source = DOSSIER / f"a_traduire_{langue}.json"
    annonces = json.loads(source.read_text(encoding="utf-8"))
    if limite:
        annonces = annonces[:limite]

    code_cible, code_fr = CODES[langue], CODES["francais"]
    acceptees, rejetees = [], []

    for i, annonce in enumerate(annonces, 1):
        texte_fr = annonce["transcript_source_fr"]
        traduction = traducteur.traduire(texte_fr, code_fr, code_cible)
        retro = traducteur.traduire(traduction, code_cible, code_fr)
        ok, raisons = controler(annonce, traduction, retro)

        commun = {
            "id": annonce["id"],
            "texte_source_fr": texte_fr,
            "retro_traduction": retro,
            "modele": MODELE_VERSION,
        }
        if ok:
            acceptees.append({
                **{c: annonce[c] for c in ("id", "slots", "pret_attendu", "piege")},
                "transcript": traduction,          # la traduction devient le texte
                "source": "traduit_auto",
                "annotateur": annonce.get("annotateur", "TZ"),
                "langue_cible": langue,
                **{k: v for k, v in commun.items() if k != "id"},
            })
        else:
            rejetees.append({**commun, "langue": langue,
                             "traduction": traduction, "raisons": raisons})

        etat = "OK " if ok else "REJET"
        print(f"  [{i:>2}/{len(annonces)}] {etat} id={annonce['id']}"
              + ("" if ok else f"  {raisons[0]}"))

    sortie = DOSSIER / f"briefs_{langue}_auto.json"
    sortie.write_text(json.dumps(acceptees, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    return acceptees, rejetees, len(annonces)


def main():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--langue", choices=["yoruba", "hausa"],
                         help="une seule langue (par défaut : les deux)")
    parseur.add_argument("--limite", type=int,
                         help="ne traiter que les N premières annonces")
    args = parseur.parse_args()

    langues = [args.langue] if args.langue else ["yoruba", "hausa"]
    traducteur = Traducteur()
    tous_rejets, taux = [], {}

    for langue in langues:
        print(f"\n=== {langue} ===")
        acceptees, rejetees, total = traiter_langue(langue, traducteur, args.limite)
        tous_rejets += rejetees
        taux[langue] = (len(acceptees), len(rejetees), total)

    # Les rejets des deux langues vont dans un seul fichier, pour les relire
    # sans relancer le modèle.
    anciens = []
    if FICHIER_REJETS.exists():
        anciens = [r for r in json.loads(FICHIER_REJETS.read_text(encoding="utf-8"))
                   if r.get("langue") not in langues]
    FICHIER_REJETS.write_text(
        json.dumps(anciens + tous_rejets, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print("\n=== Taux d'acceptation ===")
    for langue, (ok, rejet, total) in taux.items():
        print(f"  {langue:8} {ok:>3}/{total} acceptées ({ok / total:.0%}), {rejet} rejetées")
        if ok / total < 0.5:
            print(f"           ATTENTION : sous 50 %. On ne touche pas aux règles, "
                  f"c'est un résultat à documenter.")

    print("\n=== Raisons de rejet les plus fréquentes ===")
    for famille, nombre in resumer(tous_rejets)[:5]:
        print(f"  {nombre:>3}x  {famille}")

    print(f"\nRejets détaillés -> {FICHIER_REJETS.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
