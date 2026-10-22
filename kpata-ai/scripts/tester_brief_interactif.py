"""Saisie interactive pour tester le schéma, la complétude et la génération."""
import sys
from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET / "src"))

from kpata.completude import SEUIL, champs_manquants, completude, pret_pour_generation
from kpata.generation_texte import generer_texte_publicitaire
from kpata.normalisation import normaliser_brief
from kpata.schema import CHAMPS, INTENTS, MEDIAS, POIDS_PAR_INTENTION, TONS, nouveau_brief
from kpata.validation import valider_brief

EXEMPLES = {
    "language": "francais, yoruba ou hausa",
    "intent": "choisir un numéro dans la liste",
    "business_name": "ex. Chez Awa",
    "business_type": "ex. boutique de chaussures",
    "product": "ex. chaussures ou coiffure",
    "event_name": "ex. journée portes ouvertes",
    "promotion": "ex. 20% ou 10 000 F",
    "price": "ex. 2500 ou 5 000 F",
    "currency": "XOF ou NGN",
    "start_date": "ex. samedi ou 15 octobre",
    "end_date": "ex. dimanche ou 20 octobre",
    "location": "ex. Cotonou",
    "phone": "ex. 0197000000 ou +234 803 123 4567",
    "tone": ", ".join(TONS),
    "requested_media": ", ".join(MEDIAS),
}


def _lire_intention(input_fn, output_fn):
    output_fn("Intentions disponibles :")
    for numero, intent in enumerate(INTENTS, start=1):
        output_fn(f"  {numero}. {intent}")

    while True:
        valeur = input_fn("intent [numéro ou nom, vide pour omettre] : ").strip()
        if not valeur:
            return None
        if valeur.isdigit() and 1 <= int(valeur) <= len(INTENTS):
            return INTENTS[int(valeur) - 1]
        if valeur in INTENTS:
            return valeur
        output_fn("Choix inconnu : entrez un numéro de la liste ou le nom exact.")


def _lire_champs(input_fn, output_fn):
    champs = {}
    for champ in CHAMPS:
        if champ == "intent":
            champs[champ] = _lire_intention(input_fn, output_fn)
            continue
        valeur = input_fn(f"{champ} ({EXEMPLES[champ]}, vide si absent) : ").strip()
        champs[champ] = valeur or None
    return nouveau_brief(**champs)


def _afficher_manquants(manquants, output_fn):
    if not manquants:
        output_fn("Champs manquants : aucun")
        return
    affichage = [" ou ".join(item) if isinstance(item, tuple) else item
                 for item in manquants]
    output_fn("Champs manquants : " + ", ".join(affichage))


def main(input_fn=None, output_fn=None):
    """Demande un brief et affiche le résultat de chaque étape du pipeline."""
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn
    output_fn("Test interactif du schéma, du moteur de complétude et du générateur")
    output_fn("Laissez un champ vide s'il n'a pas été fourni. Ctrl+C pour quitter.\n")
    try:
        brut = _lire_champs(input_fn, output_fn)
    except (KeyboardInterrupt, EOFError):
        output_fn("\nTest interrompu.")
        return

    brief = normaliser_brief(brut)
    intent = brief.get("intent")

    output_fn("\n--- Brief normalisé ---")
    for champ in CHAMPS:
        output_fn(f"{champ}: {brief.get(champ) if brief.get(champ) is not None else '—'}")

    output_fn("\n--- Complétude ---")
    if intent in POIDS_PAR_INTENTION:
        poids = POIDS_PAR_INTENTION[intent]
        output_fn(f"Poids appliqués pour « {intent} » : " +
                  ", ".join(f"{champ}={valeur}" for champ, valeur in poids.items()))
    output_fn(f"Score : {completude(brief):.0%} (seuil : {SEUIL:.0%})")
    _afficher_manquants(champs_manquants(brief), output_fn)
    feu_vert = pret_pour_generation(brief)
    output_fn(f"Feu vert du moteur : {'oui' if feu_vert else 'non'}")

    output_fn("\n--- Validation ---")
    invalides = valider_brief(brief)
    if invalides:
        for champ, message in invalides.items():
            output_fn(f"{champ}: {message}")
    else:
        output_fn("Aucune valeur présente invalide.")

    if not feu_vert or invalides:
        output_fn("\nGénération ignorée : corrigez les champs manquants ou invalides.")
        return

    output_fn("\n--- Texte publicitaire généré ---")
    try:
        output_fn(generer_texte_publicitaire(brief))
    except ValueError as erreur:
        output_fn(f"Génération refusée : {erreur}")


if __name__ == "__main__":
    main()
