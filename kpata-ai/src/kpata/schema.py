"""Schéma du brief publicitaire : champs, valeurs et règles par intention."""

INTENTS = ["promotion", "lancement", "ouverture", "evenement",
           "restock", "annonce_service", "offre_limitee"]
TONS = ["chaleureux", "festif", "professionnel", "luxe"]
MEDIAS = ["poster_whatsapp", "poster_portrait", "statut_whatsapp", "texte_publication"]

CHAMPS = ["language", "intent", "business_name", "business_type", "product",
          "event_name", "promotion", "price", "currency", "start_date", "end_date",
          "location", "phone", "tone", "requested_media"]

# Poids de référence exposés pour les annotations et les anciens appelants.
POIDS = {"phone": 3, "product": 3, "event_name": 3, "promotion": 3, "price": 3,
         "location": 3, "start_date": 2, "business_name": 1, "business_type": 1,
         "end_date": 1, "tone": 1, "requested_media": 1, "currency": 1}

POIDS_PAR_INTENTION = {
    "promotion": {
        "phone": 3, "location": 3, "product": 3, "promotion": 3, "price": 3,
        "start_date": 2, "end_date": 1, "business_name": 1, "business_type": 1,
        "currency": 1, "tone": 1, "requested_media": 1,
    },
    "offre_limitee": {
        "phone": 3, "location": 3, "product": 3, "promotion": 3, "price": 3,
        "start_date": 3, "end_date": 2, "business_name": 1, "business_type": 1,
        "currency": 1, "tone": 1, "requested_media": 1,
    },
    "lancement": {
        "phone": 3, "location": 3, "product": 3, "price": 2, "currency": 1,
        "start_date": 2, "business_name": 1, "business_type": 1,
        "tone": 1, "requested_media": 1,
    },
    "ouverture": {
        "phone": 3, "location": 3, "business_name": 3, "business_type": 3,
        "start_date": 2, "end_date": 1, "tone": 1, "requested_media": 1,
    },
    "evenement": {
        "phone": 3, "location": 3, "event_name": 3, "start_date": 3,
        "end_date": 2, "business_name": 1, "business_type": 1,
        "tone": 1, "requested_media": 1,
    },
    "restock": {
        "phone": 3, "location": 3, "product": 3, "price": 2, "currency": 1,
        "business_name": 1, "business_type": 1, "tone": 1, "requested_media": 1,
    },
    "annonce_service": {
        "phone": 3, "location": 3, "product": 3, "business_type": 2,
        "business_name": 1, "price": 1, "currency": 1, "tone": 1,
        "requested_media": 1,
    },
}

BASE = ["location", "phone"]
OBLIGATOIRES = {
    "promotion": ["product", ("promotion", "price"), *BASE],
    "offre_limitee": ["product", ("promotion", "price"),
                      ("start_date", "end_date"), *BASE],
    "lancement": ["product", *BASE],
    "ouverture": [("business_name", "business_type"), *BASE],
    "evenement": ["event_name", "start_date", *BASE],
    "restock": ["product", *BASE],
    "annonce_service": ["product", *BASE],
}
SOUHAITES = ["business_name", "business_type", "start_date", "end_date", "currency",
             "tone", "requested_media"]


def nouveau_brief(**champs):
    """Construit un brief vide avec les champs du schéma."""
    inconnus = set(champs) - set(CHAMPS)
    if inconnus:
        raise ValueError(f"champ inconnu : {inconnus}")
    return {champ: champs.get(champ) for champ in CHAMPS}
