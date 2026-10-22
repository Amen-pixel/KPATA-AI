"""Moteur de complétude et feu vert de génération des briefs."""
from .schema import OBLIGATOIRES, POIDS_PAR_INTENTION

SEUIL = 0.5
SEUIL_PROPOSE = 0.6


def _membres(item):
    return (item,) if isinstance(item, str) else item


def _est_rempli(valeur):
    return bool(valeur) and (not isinstance(valeur, str) or bool(valeur.strip()))


def _present(brief, item):
    return any(_est_rempli(brief.get(champ)) for champ in _membres(item))


def _poids(intent, item):
    poids = POIDS_PAR_INTENTION[intent]
    return max(poids.get(champ, 0) for champ in _membres(item))


def champs_manquants(brief):
    """Retourne les champs d'entrée et obligatoires qui ne sont pas renseignés."""
    manque = [champ for champ in ("language", "intent")
              if not _est_rempli(brief.get(champ))]
    if brief.get("intent") in OBLIGATOIRES:
        manque += [item for item in OBLIGATOIRES[brief["intent"]]
                   if not _present(brief, item)]
    return manque


def completude(brief):
    """Calcule le poids des champs utiles renseignés divisé par leur poids total."""
    if not _est_rempli(brief.get("language")) or brief.get("intent") not in OBLIGATOIRES:
        return 0.0
    intent = brief["intent"]
    poids = POIDS_PAR_INTENTION[intent]
    obligatoires = OBLIGATOIRES[intent]
    deja = {champ for item in obligatoires for champ in _membres(item)}
    items = obligatoires + [
        champ for champ, valeur in poids.items()
        if champ not in deja and valeur > 0
    ]
    total = sum(_poids(intent, item) for item in items)
    return (sum(_poids(intent, item) for item in items if _present(brief, item)) / total
            if total else 0.0)


def pret_pour_generation(brief):
    """Indique si le brief remplit les règles et le seuil du feu vert."""
    return (brief.get("intent") in OBLIGATOIRES
            and not champs_manquants(brief)
            and completude(brief) >= SEUIL)
