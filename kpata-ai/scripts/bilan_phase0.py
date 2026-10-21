"""Bilan de la Phase 0 (tâche E).

Fait passer toutes les annonces annotées dans la chaîne
normaliser -> valider -> feu vert, puis écrit docs/bilan_phase0.md.

Usage, depuis la racine du dépôt :
    python scripts/bilan_phase0.py

Le script ne modifie aucune donnée : il lit, mesure et écrit un rapport.
"""
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from kpata.brief import (CHAMPS, INTENTS, POIDS, SEUIL, champs_manquants, completude,
                         pret_pour_generation)
from kpata.normalisation import NORMALISEURS, normaliser_brief
from kpata.validation import valider_brief

RACINE = Path(__file__).parent.parent
DOSSIER_BRIEFS = RACINE / "data" / "briefs"
RAPPORT = RACINE / "docs" / "bilan_phase0.md"

# Champs critiques au sens du cahier §7.2 et du QA Agent §12.
CRITIQUES = ["price", "promotion", "start_date", "phone", "location", "product", "business_name"]


# --------------------------------------------------------------------------- #
# Lecture
# --------------------------------------------------------------------------- #
def charger():
    """Toutes les annonces de data/briefs/, avec le nom de leur fichier."""
    annonces = []
    for chemin in sorted(DOSSIER_BRIEFS.glob("*.json")):
        for annonce in json.loads(chemin.read_text(encoding="utf-8")):
            annonces.append({**annonce, "_fichier": chemin.name})
    return annonces


def analyser(annonce):
    """Passe une annonce dans la chaîne complète et renvoie le détail."""
    slots = annonce["slots"]
    brief = normaliser_brief(slots)
    manquants = champs_manquants(brief)
    invalides = valider_brief(brief)
    pret = pret_pour_generation(brief) and not invalides

    # Valeurs que la normalisation n'a pas su traiter : elle a laissé la valeur
    # d'origine au lieu de renvoyer une forme standard.
    echecs = []
    for champ, fonction in NORMALISEURS.items():
        brut = slots.get(champ)
        if brut and fonction(brut) is None:
            echecs.append((champ, brut))

    return {
        "id": annonce["id"],
        "fichier": annonce["_fichier"],
        "langue": slots.get("language"),
        "intent": slots.get("intent"),
        "source": annonce.get("source", "inconnue"),
        "annotateur": annonce.get("annotateur", "?"),
        "c": completude(brief),
        "pret": pret,
        "pret_attendu": annonce["pret_attendu"],
        "accord": pret == annonce["pret_attendu"],
        "manquants": [m if isinstance(m, str) else " ou ".join(m) for m in manquants],
        "invalides": dict(invalides),
        "echecs_normalisation": echecs,
        "piege": annonce.get("piege", ""),
        "slots_remplis": [c for c in CHAMPS if slots.get(c)],
    }


# --------------------------------------------------------------------------- #
# Mise en forme
# --------------------------------------------------------------------------- #
def tableau(entetes, lignes):
    if not lignes:
        return "_Aucune donnée._\n"
    out = ["| " + " | ".join(entetes) + " |",
           "| " + " | ".join("---" for _ in entetes) + " |"]
    out += ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]
    return "\n".join(out) + "\n"


def stats(valeurs):
    """(minimum, moyenne, maximum) ou des tirets si la liste est vide."""
    if not valeurs:
        return "—", "—", "—"
    return (f"{min(valeurs):.2f}", f"{sum(valeurs) / len(valeurs):.2f}", f"{max(valeurs):.2f}")


def ecrire_rapport(resultats):
    total = len(resultats)
    parties = [
        "# Bilan de la Phase 0 — Kpata AI",
        "",
        f"Généré automatiquement par `scripts/bilan_phase0.py` le {date.today():%d/%m/%Y}.",
        "Ne pas modifier à la main : relancer le script.",
        "",
        f"**{total} annonces analysées**, seuil du feu vert en vigueur : **{SEUIL}**.",
        "",
        "---",
        "",
    ]

    # 1. Volumes
    par_langue = Counter(r["langue"] for r in resultats)
    parties += ["## 1. Nombre d'annonces", "", "### Par langue", "",
                tableau(["Langue", "Annonces"],
                        [[lg, n] for lg, n in sorted(par_langue.items())]), ""]

    croise = defaultdict(Counter)
    for r in resultats:
        croise[r["intent"]][r["langue"]] += 1
    langues = sorted(par_langue)
    parties += ["### Par intention et par langue", "",
                tableau(["Intention"] + langues + ["Total"],
                        [[i] + [croise[i][lg] for lg in langues] + [sum(croise[i].values())]
                         for i in INTENTS]), ""]

    par_source = Counter(r["source"] for r in resultats)
    parties += ["### Par origine du texte", "",
                tableau(["Source", "Annonces"],
                        [[s, n] for s, n in sorted(par_source.items())]),
                "",
                "> `a_traduire` : texte source en français, en attente d'un locuteur natif. "
                "Ces annonces ne sont pas utilisables pour mesurer une performance par langue.",
                "", "---", ""]

    # 2. Feu vert
    prets = [r for r in resultats if r["pret"]]
    accords = [r for r in resultats if r["accord"]]
    desaccords = [r for r in resultats if not r["accord"]]
    parties += ["## 2. Feu vert : calculé contre attendu", "",
                tableau(["Mesure", "Nombre", "Part"],
                        [["Prêtes pour la génération", len(prets), f"{len(prets) / total:.0%}"],
                         ["Non prêtes", total - len(prets), f"{1 - len(prets) / total:.0%}"],
                         ["**Accords** avec `pret_attendu`", len(accords), f"{len(accords) / total:.0%}"],
                         ["**Désaccords**", len(desaccords), f"{len(desaccords) / total:.0%}"]]),
                ""]
    if desaccords:
        parties += ["### Détail des désaccords", "",
                    tableau(["Fichier", "id", "Calculé", "Attendu", "C", "Cause"],
                            [[r["fichier"], r["id"], r["pret"], r["pret_attendu"], f"{r['c']:.2f}",
                              (", ".join(r["manquants"]) or ", ".join(r["invalides"]) or r["piege"])[:60]]
                             for r in desaccords]), ""]
    else:
        parties += ["Aucun désaccord : le moteur donne exactement le feu vert attendu "
                    "sur l'ensemble des annonces.", ""]
    parties += ["---", ""]

    # 3. Champs manquants
    manquants = Counter(m for r in resultats for m in r["manquants"])
    parties += ["## 3. Champs qui manquent le plus souvent", "",
                tableau(["Champ", "Annonces concernées", "Poids dans C"],
                        [[c, n, POIDS.get(c, "—")] for c, n in manquants.most_common()])
                if manquants else "Aucun champ obligatoire ne manque.\n", ""]

    jamais = [c for c in CRITIQUES
              if not any(c in r["slots_remplis"] for r in resultats)]
    rempli = {c: sum(1 for r in resultats if c in r["slots_remplis"]) for c in CHAMPS}
    parties += ["### Taux de remplissage de chaque champ", "",
                tableau(["Champ", "Rempli", "Part"],
                        [[c, rempli[c], f"{rempli[c] / total:.0%}"]
                         for c in sorted(CHAMPS, key=lambda x: -rempli[x])]), ""]
    if jamais:
        parties += [f"> Champs critiques jamais renseignés : {', '.join(jamais)}.", ""]
    parties += ["---", ""]

    # 4. Échecs de normalisation
    echecs = [(r["fichier"], r["id"], champ, brut)
              for r in resultats for champ, brut in r["echecs_normalisation"]]
    par_champ = Counter(champ for _, _, champ, _ in echecs)
    parties += ["## 4. Valeurs que la normalisation n'a pas traitées", "",
                f"**{len(echecs)} valeurs** sur {total} annonces. Une valeur non traitée "
                "n'est pas forcément un bug : la plupart sont des cas invalides "
                "volontaires, que la validation doit refuser.", ""]
    if par_champ:
        parties += [tableau(["Champ", "Valeurs non traitées"],
                            [[c, n] for c, n in par_champ.most_common()]), "",
                    "### Exemples", "",
                    tableau(["Fichier", "id", "Champ", "Valeur brute"],
                            [[f, i, c, f"`{v}`"] for f, i, c, v in echecs[:20]]), ""]
        if len(echecs) > 20:
            parties += [f"_({len(echecs) - 20} autres valeurs non listées.)_", ""]
    else:
        parties += ["Aucune valeur n'a échoué à la normalisation.", ""]
    parties += ["---", ""]

    # 5. Scores C
    tous = [r["c"] for r in resultats]
    mini, moy, maxi = stats(tous)
    parties += ["## 5. Répartition des scores de complétude C", "",
                f"Sur l'ensemble : **minimum {mini}**, **moyenne {moy}**, **maximum {maxi}**.", "",
                "### Par intention", "",
                tableau(["Intention", "Annonces", "C min", "C moyen", "C max"],
                        [[i, len(cs), *stats(cs)]
                         for i in INTENTS
                         for cs in [[r["c"] for r in resultats if r["intent"] == i]]]), "",
                "### Par langue", "",
                tableau(["Langue", "Annonces", "C min", "C moyen", "C max"],
                        [[lg, len(cs), *stats(cs)]
                         for lg in langues
                         for cs in [[r["c"] for r in resultats if r["langue"] == lg]]]), ""]

    tranches = Counter()
    for c in tous:
        borne = min(int(c * 10) / 10, 0.9)
        tranches[borne] += 1
    parties += ["### Distribution", "",
                tableau(["Tranche de C", "Annonces"],
                        [[f"{b:.1f} à {b + 0.1:.1f}", tranches[b]]
                         for b in sorted(tranches)]), "",
                f"Annonces sous le seuil ({SEUIL}) : "
                f"**{sum(1 for c in tous if c < SEUIL)}** sur {total}.", "", "---", ""]

    # 6. Accord entre annotateurs
    par_annotateur = Counter(r["annotateur"] for r in resultats)
    parties += ["## 6. Annotation", "",
                tableau(["Annotateur", "Annonces", "Accords moteur/attendu"],
                        [[a, n, sum(1 for r in resultats
                                    if r["annotateur"] == a and r["accord"])]
                         for a, n in sorted(par_annotateur.items())]), "",
                "> La double annotation (1 annonce sur 5) n'a pas encore été faite : "
                "les annonces ont un seul annotateur. Le taux d'accord entre "
                "annotateurs sera mesuré ici dès que la seconde passe sera faite.",
                "", "---", ""]

    # 7. Génération de texte : réservé à Eudes
    parties += ["## 7. Générateur de texte (à compléter par Eudes)", "",
                "_Section réservée._ Le générateur de texte à base de templates "
                "(cahier §5) n'est pas encore disponible. Quand il le sera, cette "
                "section devra présenter :", "",
                "- le nombre de campagnes générées sans intervention humaine ;",
                "- les champs critiques correctement reportés sur l'affiche "
                "(`CriticalFieldAccuracy`, cahier §7.2) ;",
                "- les cas où le texte généré a inventé une information absente du brief ;",
                "- le résultat du QA Agent (cahier §12) sur chaque campagne.", "",
                "---", ""]

    # 8. Reste à faire
    a_traduire = par_source.get("a_traduire", 0)
    parties += ["## 8. Ce qui reste à faire avant la Phase 1", "",
                "### Bloquant", "",
                f"1. **Faire traduire les {a_traduire} annonces** en Yorùbá et en Hausa "
                "par des locuteurs natifs. Sans elles, le projet n'a aucune donnée "
                "dans ses langues cibles, et l'évaluation séparée par langue exigée "
                "au §9 du cahier est impossible. Il faut identifier un locuteur "
                "Yorùbá et un locuteur Hausa.",
                "2. **Valider les décisions en attente** de `docs/decisions.md` : "
                "elles sont toutes au statut « proposé ». Les plus structurantes "
                "sont le barème des poids et le seuil (D-005), car le code des "
                "trois membres en dépend.", "",
                "### À faire", "",
                "3. **Double annotation** d'une annonce sur cinq, puis mesure du "
                "taux d'accord par champ (section 6).",
                "4. **Enregistrer les notes vocales** : `audio_path` est vide "
                "partout, les annonces sont écrites à la main. La Phase 1 demande "
                "de vrais enregistrements, avec un identifiant de locuteur anonymisé "
                "pour permettre les splits par locuteur.",
                "5. **Tableau de référence du jeu de données** "
                "(`data/tableau_reference/`), attendu en Phase 1.",
                "6. **Générateur de texte à base de templates** (cahier §5), qui "
                "complétera la section 7 de ce bilan.", "",
                "### Points de vigilance", "",
                "7. Les annonces sont **écrites par l'équipe**, donc plus propres "
                "que de vraies transcriptions. Les scores de cette page sont "
                "optimistes : l'ASR de la Phase 1 produira des textes bruités, avec "
                "des champs manquants que l'annotation manuelle capture sans peine.",
                "8. Le **seuil devra être réévalué** sur les 150 annonces traduites, "
                "puis sur de vraies transcriptions.", ""]

    RAPPORT.write_text("\n".join(parties), encoding="utf-8")
    return resultats, desaccords


def main():
    annonces = charger()
    if not annonces:
        raise SystemExit(f"Aucune annonce trouvée dans {DOSSIER_BRIEFS}")
    resultats = [analyser(a) for a in annonces]
    _, desaccords = ecrire_rapport(resultats)
    print(f"{len(resultats)} annonces analysées")
    print(f"{sum(1 for r in resultats if r['pret'])} prêtes, "
          f"{len(desaccords)} désaccord(s) avec pret_attendu")
    print("rapport écrit ->", RAPPORT.relative_to(RACINE))


if __name__ == "__main__":
    main()
