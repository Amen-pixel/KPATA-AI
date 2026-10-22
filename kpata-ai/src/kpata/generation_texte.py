"""Génération de textes publicitaires français à partir d'un brief validé."""
from collections.abc import Mapping

from .completude import champs_manquants, pret_pour_generation
from .normalisation import normaliser_brief
from .schema import CHAMPS
from .validation import valider_brief

SYMBOLES_DEVISE = {"XOF": "F CFA", "NGN": "₦"}


def _texte(brief, champ):
    valeur = brief.get(champ)
    return str(valeur).strip() if valeur is not None and str(valeur).strip() else None


def _prix(brief):
    prix = brief.get("price")
    if prix is None:
        return None
    montant = f"{prix:,}".replace(",", " ") if isinstance(prix, int) else str(prix)
    devise = SYMBOLES_DEVISE.get(_texte(brief, "currency"))
    return f"{montant} {devise}" if devise else montant


def _dates(brief):
    debut = _texte(brief, "start_date")
    fin = _texte(brief, "end_date")
    if debut and fin:
        return f"Du {debut} au {fin}."
    if debut:
        return f"À partir du {debut}."
    if fin:
        return f"Jusqu'au {fin}."
    return None


def _contenu(brief):
    intention = brief["intent"]
    produit = _texte(brief, "product")
    promotion = _texte(brief, "promotion")
    event_name = _texte(brief, "event_name")
    prix = _prix(brief)
    nom = _texte(brief, "business_name")
    type_commerce = _texte(brief, "business_type")
    date_debut = _texte(brief, "start_date")

    if intention == "promotion":
        titre = "OFFRE SPÉCIALE"
        accroche = (f"{promotion} sur {produit}" if promotion
                    else f"{produit} au prix de {prix}")
        details = [_dates(brief)]
        if promotion and prix:
            details.append(f"Prix : {prix}.")
    elif intention == "offre_limitee":
        titre = "OFFRE LIMITÉE"
        accroche = (f"{promotion} sur {produit}" if promotion
                    else f"{produit} au prix de {prix}")
        details = [_dates(brief)]
    elif intention == "lancement":
        titre = "NOUVEAUTÉ"
        accroche = f"{produit} fait son entrée dans notre offre."
        details = []
        if prix:
            details.append(f"Prix : {prix}.")
    elif intention == "ouverture":
        titre = "OUVERTURE"
        accroche = (f"Ouverture de {nom}." if nom
                    else f"Ouverture de votre {type_commerce}.")
        details = [f"À partir du {date_debut}." if date_debut else None]
    elif intention == "evenement":
        titre = "RENDEZ-VOUS"
        accroche = f"{event_name} à {brief['location']} le {date_debut}."
        details = []
    elif intention == "restock":
        titre = "DE RETOUR"
        accroche = f"{produit} est de nouveau disponible."
        details = [f"Prix : {prix}." if prix else None]
    else:
        titre = "NOS SERVICES"
        accroche = f"Découvrez notre offre de {produit}."
        details = [f"Prix : {prix}." if prix else None]

    ton = _texte(brief, "tone")
    signatures = {
        "chaleureux": "Au plaisir de vous accueillir !",
        "festif": "Venez nombreux !",
        "professionnel": "Pour toute information, contactez-nous.",
        "luxe": "Découvrez notre offre.",
    }

    lignes = []
    if nom:
        lignes.append(nom)
    lignes.extend((titre, accroche))
    lignes.extend(detail for detail in details if detail)
    if ton in signatures:
        lignes.append(signatures[ton])
    lignes.extend((f"Lieu : {brief['location']}", f"Contact : {brief['phone']}"))
    return "\n".join(lignes)


def generer_texte_publicitaire(brief: Mapping[str, object]) -> str:
    """Génère une annonce en français, sans compléter les informations absentes.

    Le brief est normalisé puis contrôlé. Les briefs incomplets ou comportant
    des valeurs invalides sont refusés avec une erreur explicite.
    """
    inconnus = set(brief) - set(CHAMPS)
    if inconnus:
        raise ValueError(f"champ inconnu : {', '.join(sorted(inconnus))}")
    if isinstance(brief.get("price"), (bool, float)):
        raise ValueError("brief invalide : price: prix doit être un entier")

    normalise = normaliser_brief(brief)
    invalides = valider_brief(normalise)
    if invalides:
        details = "; ".join(f"{champ}: {message}" for champ, message in invalides.items())
        raise ValueError(f"brief invalide : {details}")
    if not pret_pour_generation(normalise):
        manquants = ", ".join(str(champ) for champ in champs_manquants(normalise))
        raise ValueError(f"brief incomplet : {manquants}")

    return _contenu(normalise)
