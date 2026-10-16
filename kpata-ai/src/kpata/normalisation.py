# Kpata AI - Phase 0 : normalisation (téléphone, prix, pourcentage, promotion, dates, langue)
# Principe : si on n'est pas sûr, on renvoie None. On n'invente jamais une information.
import calendar
import re
import unicodedata

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def sans_accent(texte):
    """'Février' -> 'fevrier' (minuscules, sans accents)"""
    t = unicodedata.normalize("NFKD", str(texte).replace("’", "'"))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


MOIS_SA = [sans_accent(m) for m in MOIS]


def normaliser_telephone(texte):
    """'97 00 00 00', '0197000000', '+229 01 97 00 00 00' -> '+2290197000000'"""
    chiffres = re.sub(r"\D", "", str(texte))
    if chiffres.startswith("00229"):
        chiffres = chiffres[5:]
    elif chiffres.startswith("229") and len(chiffres) in (11, 13):
        chiffres = chiffres[3:]
    if len(chiffres) == 8:                       # ancien format -> on ajoute le 01
        chiffres = "01" + chiffres
    if len(chiffres) == 10 and chiffres.startswith("01"):
        return "+229" + chiffres
    return None


def normaliser_prix(texte):
    """'5 000 F', '5000 fcfa', '5.000 CFA' -> 5000"""
    m = re.search(r"(\d[\d\s.,]*)\s*(fcfa|cfa|francs?|f)\b", str(texte).lower())
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def normaliser_pourcentage(texte):
    """'20%', '-20 %', '20 pour cent' -> '-20 %'  (entre 1 et 100 seulement)"""
    m = re.search(r"(\d{1,3})\s*(%|pour\s?cent)", str(texte).lower())
    if m and 1 <= int(m.group(1)) <= 100:
        return f"-{int(m.group(1))} %"
    return None


def normaliser_promotion(texte):
    """'20%' -> '-20 %' ; '10 000 F de réduction' -> '-10000 F'"""
    pct = normaliser_pourcentage(texte)
    if pct:
        return pct
    prix = normaliser_prix(texte)
    return f"-{prix} F" if prix else None


def extraire_dates(texte):
    """'samedi', 'demain', 'ce week-end', '15 octobre', '15/10' -> liste dans l'ordre du texte"""
    t = sans_accent(texte)
    trouves = []
    motif = r"\b(" + "|".join(JOURS) + r"|demain|aujourd'hui|week-?end)\b"
    for m in re.finditer(motif, t):
        mot = m.group(1)
        trouves.append((m.start(), "week-end" if mot.startswith("week") else mot))
    for m in re.finditer(r"\b(\d{1,2})(?:er)?\s+(" + "|".join(MOIS_SA) + r")\b", t):
        trouves.append((m.start(), (int(m.group(1)), MOIS_SA.index(m.group(2)) + 1)))
    for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})\b", t):
        trouves.append((m.start(), (int(m.group(1)), int(m.group(2)))))
    dates = []
    for _, v in sorted(trouves, key=lambda x: x[0]):
        if isinstance(v, str):
            dates.append(v)
        else:
            jour, mois = v                       # on vérifie que la date existe (30 février -> refusé)
            if 1 <= mois <= 12 and 1 <= jour <= calendar.monthrange(2024, mois)[1]:
                dates.append(f"{jour} {MOIS[mois - 1]}")
    return dates


def normaliser_date(texte):
    dates = extraire_dates(texte)
    return dates[0] if dates else None


ALIAS_LANGUES = {"yoruba": "yoruba", "yorouba": "yoruba", "hausa": "hausa",
                 "haoussa": "hausa", "francais": "francais", "fr": "francais"}


def normaliser_langue(texte):
    """'Yorùbá' -> 'yoruba', 'Français' -> 'francais'"""
    return ALIAS_LANGUES.get(sans_accent(texte).strip())


NORMALISEURS = {"phone": normaliser_telephone, "promotion": normaliser_promotion,
                "price": normaliser_prix, "start_date": normaliser_date,
                "end_date": normaliser_date, "language": normaliser_langue}


def normaliser_brief(brief):
    """Met chaque champ sous sa forme standard. Si impossible, on garde la valeur
    telle quelle : c'est la validation qui la refusera."""
    propre = dict(brief)
    for champ, fonction in NORMALISEURS.items():
        if brief.get(champ):
            propre[champ] = fonction(brief[champ]) or brief[champ]
    return propre


if __name__ == "__main__":
    print("tel   :", [normaliser_telephone(x) for x in ["0197000000", "97 00 00 00", "+229 97 11 22 33", "12345"]])
    print("prix  :", [normaliser_prix(x) for x in ["5 000 F", "5.000 CFA", "gratuit"]])
    print("promo :", [normaliser_promotion(x) for x in ["20 pour cent", "10 000 F de réduction", "150%"]])
    print("dates :", [normaliser_date(x) for x in ["vendredi", "le 15 octobre", "15/10", "1er novembre",
                                                    "ce week-end", "30 février", "vendradi"]])
    print("langue:", [normaliser_langue(x) for x in ["Yorùbá", "Haoussa", "Français", "swahili"]])
