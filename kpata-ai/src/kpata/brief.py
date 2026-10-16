# Kpata AI - Phase 0 : schéma du brief, score de complétude C, feu vert pour la génération
# Cahier des charges : §4 (objet structuré), §5 (score C), §6 (schéma), §7.2 (champs prioritaires)

INTENTS = ["promotion", "lancement", "ouverture", "evenement",
           "restock", "annonce_service", "offre_limitee"]
TONS = ["chaleureux", "festif", "professionnel", "luxe"]
MEDIAS = ["poster_whatsapp", "poster_portrait", "statut_whatsapp", "texte_publication"]

# Tous les champs d'un brief
CHAMPS = ["language", "intent", "business_name", "business_type", "product",
          "promotion",   # la réduction : "-20 %" ou "-10000 F"
          "price",       # un prix affiché : 2500
          "start_date", "end_date", "location", "phone", "tone", "requested_media"]

# Poids : plus un champ compte sur l'affiche, plus il pèse dans le score C
POIDS = {"phone": 3, "product": 3, "promotion": 3, "price": 3, "location": 2,
         "business_name": 2, "start_date": 2, "business_type": 1, "end_date": 1,
         "tone": 1, "requested_media": 1}

# Champs OBLIGATOIRES selon l'intention. Un tuple = "au moins un des deux".
BASE = ["location", "phone"]
OBLIGATOIRES = {
    "promotion":       ["product", ("promotion", "price"), *BASE],
    "offre_limitee":   ["product", ("promotion", "price"), ("start_date", "end_date"), *BASE],
    "lancement":       ["product", *BASE],
    "ouverture":       [("business_name", "business_type"), *BASE],
    "evenement":       ["start_date", *BASE],
    "restock":         ["product", *BASE],
    "annonce_service": ["product", *BASE],
}
SOUHAITES = ["business_name", "business_type", "start_date", "end_date", "tone", "requested_media"]
SEUIL = 0.5


def _membres(item):
    return (item,) if isinstance(item, str) else item


def _present(brief, item):
    return any(brief.get(c) for c in _membres(item))


def _poids(item):
    return max(POIDS.get(c, 0) for c in _membres(item))


def champs_manquants(brief):
    """Ce que la personne n'a pas dit (et dont on a besoin)."""
    manque = [c for c in ("language", "intent") if not brief.get(c)]
    if brief.get("intent") in OBLIGATOIRES:
        manque += [i for i in OBLIGATOIRES[brief["intent"]] if not _present(brief, i)]
    return manque


def completude(brief):
    """C = somme des poids des champs présents / somme des poids des champs utiles"""
    obligatoires = OBLIGATOIRES.get(brief.get("intent"), [])
    deja = {c for i in obligatoires for c in _membres(i)}
    items = obligatoires + [c for c in SOUHAITES if c not in deja]
    total = sum(_poids(i) for i in items)
    return sum(_poids(i) for i in items if _present(brief, i)) / total if total else 0.0


def pret_pour_generation(brief):
    return (brief.get("intent") in OBLIGATOIRES
            and not champs_manquants(brief)
            and completude(brief) >= SEUIL)


def nouveau_brief(**champs):
    """Un brief vide avec tous les champs (refuse les champs inconnus)."""
    inconnus = set(champs) - set(CHAMPS)
    if inconnus:
        raise ValueError(f"champ inconnu : {inconnus}")
    return {c: champs.get(c) for c in CHAMPS}


if __name__ == "__main__":
    promo = nouveau_brief(language="francais", intent="promotion", business_type="boutique de chaussures",
                          product="chaussures", promotion="-20 %", location="Abomey-Calavi",
                          phone="+2290197000000", start_date="vendredi", end_date="samedi")
    restock = nouveau_brief(language="francais", intent="restock", product="wax",
                            location="Dantokpa", phone="+2290196000000")
    sans_tel = {**promo, "phone": None}
    for nom, b in [("promo complète", promo), ("restock sans promo", restock), ("promo sans téléphone", sans_tel)]:
        print(f"{nom:22} C = {completude(b):.2f} | prêt : {pret_pour_generation(b)} | manque : {champs_manquants(b)}")
