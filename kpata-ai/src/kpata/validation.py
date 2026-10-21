# Kpata AI - Phase 0 : règles de validation des champs
from .brief import INTENTS, TONS, MEDIAS
from .normalisation import (DEVISES, normaliser_telephone, normaliser_prix,
                            normaliser_promotion, normaliser_date, normaliser_langue)


def texte_min(n):
    return lambda v: len(str(v).strip()) >= n


# champ -> (règle qui renvoie True si c'est valide, message pour la personne)
REGLES = {
    "language":      (lambda v: normaliser_langue(v) is not None, "langue inconnue (yoruba, hausa ou francais)"),
    "intent":        (lambda v: v in INTENTS, "type de demande inconnu"),
    "business_name": (texte_min(2), "nom du commerce trop court"),
    "business_type": (texte_min(3), "type de commerce trop court"),
    "product":       (texte_min(2), "produit trop court"),
    "promotion":     (lambda v: normaliser_promotion(v) is not None, "réduction invalide (ex : 20 % ou 10 000 F)"),
    "price":         (lambda v: (isinstance(v, int) and v > 0) or normaliser_prix(v, champ="price") is not None, "prix invalide"),
    "currency":      (lambda v: v in DEVISES, "devise inconnue (XOF ou NGN)"),
    "start_date":    (lambda v: normaliser_date(v) is not None, "date de début invalide"),
    "end_date":      (lambda v: normaliser_date(v) is not None, "date de fin invalide"),
    "location":      (texte_min(3), "lieu trop court"),
    "phone":         (lambda v: normaliser_telephone(v) is not None, "numéro de téléphone invalide"),
    "tone":          (lambda v: v in TONS, "ton inconnu"),
    "requested_media": (lambda v: v in MEDIAS, "support demandé inconnu"),
}


def valider_brief(brief):
    """Champs PRÉSENTS mais invalides -> {champ: message}. Dictionnaire vide = tout est bon."""
    return {c: msg for c, (regle, msg) in REGLES.items()
            if brief.get(c) and not regle(brief[c])}


if __name__ == "__main__":
    bon = {"language": "yoruba", "intent": "promotion", "phone": "0197000000", "promotion": "20%",
           "product": "chaussures", "location": "Calavi", "start_date": "15 octobre"}
    mauvais = {"language": "swahili", "intent": "promotion", "phone": "12345", "promotion": "150%",
               "product": "x", "start_date": "30 février"}
    print("bon     ->", valider_brief(bon))
    print("mauvais ->", valider_brief(mauvais))
