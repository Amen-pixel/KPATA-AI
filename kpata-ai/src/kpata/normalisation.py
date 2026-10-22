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


# --------------------------------------------------------------------------- #
# Téléphone : Bénin (+229), Nigeria (+234), Niger (+227)
# --------------------------------------------------------------------------- #
# Les locuteurs Yorùbá et Hausa sont surtout au Nigeria et au Niger : on doit
# accepter leurs numéros. Pour chaque pays : indicatif, longueur du numéro
# national (sans le 0 de tête) et préfixes acceptés.
PAYS_TELEPHONE = {
    "benin":   {"indicatif": "229", "longueur": 10, "prefixes": ("01",)},
    "nigeria": {"indicatif": "234", "longueur": 10, "prefixes": ("70", "80", "81", "90", "91")},
    "niger":   {"indicatif": "227", "longueur": 8,  "prefixes": ("20", "21", "22", "23",
                                                                 "80", "87", "88", "89",
                                                                 "90", "91", "92", "93",
                                                                 "94", "96", "97", "98", "99")},
}
PAYS_PAR_INDICATIF = {p["indicatif"]: nom for nom, p in PAYS_TELEPHONE.items()}
PAYS_DEFAUT = "benin"

# Villes qui permettent de lever l'ambiguïté d'un numéro à 8 chiffres sans
# indicatif (béninois en ancien format, ou nigérien). Voir docs/decisions.md.
VILLES_PAR_PAYS = {
    "niger": ["niamey", "zinder", "maradi", "tahoua", "agadez", "dosso"],
}


def detecter_pays(lieu):
    """'Niamey' -> 'niger'. Lieu inconnu ou ambigu -> None (on n'invente pas)."""
    if not lieu:
        return None
    texte = sans_accent(lieu)
    for pays, villes in VILLES_PAR_PAYS.items():
        if any(re.search(r"\b" + re.escape(v) + r"\b", texte) for v in villes):
            return pays
    return None


def _numero_valide(chiffres, pays):
    """Le numéro national correspond-il au format du pays ?"""
    regle = PAYS_TELEPHONE[pays]
    return (len(chiffres) == regle["longueur"]
            and chiffres.startswith(regle["prefixes"]))


def normaliser_telephone(texte, pays=None):
    """Met un numéro sous la forme internationale : '+229' + numéro national.

    '0197000000', '97 00 00 00'   -> '+229' + '0197000000'   (Bénin)
    '+234 803 123 4567'           -> '+234' + '8031234567'   (Nigeria)
    '+227 96 12 34 56'            -> '+227' + '96123456'     (Niger)
    '12345'                       -> None

    `pays` ne sert qu'aux numéros sans indicatif, quand la longueur est ambiguë
    (8 chiffres). Sans indication, le Bénin reste le pays par défaut.
    """
    chiffres = re.sub(r"\D", "", str(texte))
    if not chiffres:
        return None

    # 1. Indicatif explicite (+229..., 00229..., 229...) : il décide du pays.
    for prefixe_international in ("00", ""):
        reste = chiffres[len(prefixe_international):]
        for indicatif, nom in PAYS_PAR_INDICATIF.items():
            if not reste.startswith(indicatif):
                continue
            national = reste[len(indicatif):]
            if _numero_valide(national, nom):
                return "+" + indicatif + national
            # Bénin : ancien format à 8 chiffres derrière l'indicatif
            if nom == "benin" and _numero_valide("01" + national, "benin"):
                return "+" + indicatif + "01" + national

    # 2. Pas d'indicatif. On essaie le pays demandé, puis le pays par défaut.
    candidats = [pays] if pays in PAYS_TELEPHONE else []
    candidats += [p for p in (PAYS_DEFAUT, "nigeria", "niger") if p not in candidats]

    for nom in candidats:
        national = chiffres
        # Un 0 de tête est une notation nationale : '0803...' -> '803...'
        if nom == "nigeria" and national.startswith("0"):
            national = national[1:]
        if _numero_valide(national, nom):
            return "+" + PAYS_TELEPHONE[nom]["indicatif"] + national
        # Bénin : ancien format à 8 chiffres -> on ajoute le 01
        if nom == "benin" and _numero_valide("01" + national, "benin"):
            return "+229" + "01" + national

    return None


# --------------------------------------------------------------------------- #
# Prix et devise
# --------------------------------------------------------------------------- #
# Unités reconnues, par devise. XOF = franc CFA, NGN = naira.
# Deux positions : l'unité après le nombre ('5000 F') ou avant ('₦5000', 'N5000').
# Le symbole '₦' n'est pas un caractère de mot : il ne peut pas porter de \b.
UNITES_DEVISE = {
        "XOF": {"suffixe": r"(?:fcfa|cfa|francs?|f)\b", "prefixe": r"(?<![a-z])(?:fcfa|cfa|f)(?=\s*\d)"},
    "NGN": {"suffixe": r"(?:nairas?)\b|₦", "prefixe": r"₦|(?<![a-z])n(?=\s*\d)"},
}
MULTIPLICATEURS = {"mille": 1000, "millier": 1000, "milliers": 1000}
DEVISES = ("XOF", "NGN")



def _nombre(texte_nombre):
    """'5 000' ou '5.000' -> 5000. Renvoie None si aucun chiffre."""
    chiffres = re.sub(r"\D", "", texte_nombre)
    return int(chiffres) if chiffres else None


def _chercher_montant(texte, unites):
    """Cherche '<nombre> [mille] <unité>' puis '<unité> <nombre>' (₦5000, N5000)."""
    t = sans_accent(texte)
    apres = re.search(r"(\d[\d\s.,]*)\s*(mille|milliers?)?\s*(?:" + unites["suffixe"] + r")", t)
    if apres:
        valeur = _nombre(apres.group(1))
        if valeur is not None and apres.group(2):
            valeur *= MULTIPLICATEURS[apres.group(2)]
        return valeur
    avant = re.search(r"(?:" + unites["prefixe"] + r")\s*(\d[\d\s.,]*)\s*(mille|milliers?)?", t)
    if avant:
        valeur = _nombre(avant.group(1))
        if valeur is not None and avant.group(2):
            valeur *= MULTIPLICATEURS[avant.group(2)]
        return valeur
    return None


def detecter_devise(texte):
    """'5000 F' -> 'XOF' ; '₦5000' -> 'NGN' ; '3000' -> None (on n'invente pas)."""
    if isinstance(texte, (int, float)):
        return None
    # NGN d'abord : le 'n' de 'naira' est plus spécifique que le 'f' du franc.
    for devise in ("NGN", "XOF"):
        if _chercher_montant(texte, UNITES_DEVISE[devise]) is not None:
            return devise
    return None


# Champs dans lesquels un nombre seul est forcément un montant.
CHAMPS_MONTANT = ("price", "promotion")


def normaliser_prix(texte, champ=None):
    """'5 000 F', '5.000 CFA', '₦5000', '5 mille F' -> 5000 (toujours un entier).

    Un nombre seul ('3000') n'est accepté que si la valeur vient du champ
    `price` ou `promotion`. Dans un texte libre, ce pourrait être un numéro de
    téléphone : on refuse plutôt que de se tromper.
    """
    if isinstance(texte, int) and not isinstance(texte, bool):
        return texte if texte > 0 else None

    for devise in ("NGN", "XOF"):
        valeur = _chercher_montant(texte, UNITES_DEVISE[devise])
        if valeur is not None:
            return valeur

    t = sans_accent(texte).strip()

    # '5 mille' : le mot est explicite, ce n'est jamais un numéro de téléphone.
    ecrit = re.fullmatch(r"(\d[\d\s.,]*)\s*(mille|milliers?)", t)
    if ecrit:
        valeur = _nombre(ecrit.group(1))
        if valeur is not None:
            return valeur * MULTIPLICATEURS[ecrit.group(2)]

    if champ in CHAMPS_MONTANT:
        seul = re.fullmatch(r"(\d[\d\s.,]*)\s*(mille|milliers?)?", t)
        if seul:
            valeur = _nombre(seul.group(1))
            if valeur is not None and seul.group(2):
                valeur *= MULTIPLICATEURS[seul.group(2)]
            return valeur
    return None


def normaliser_pourcentage(texte):
    """'20%', '-20 %', '20 pour cent' -> '-20 %'  (entre 1 et 100 seulement)"""
    m = re.search(r"(\d{1,3})\s*(%|pour\s?cent)", sans_accent(texte))
    if m and 1 <= int(m.group(1)) <= 100:
        return f"-{int(m.group(1))} %"
    return None


# Symbole affiché pour chaque devise, dans les réductions en montant.
SYMBOLE_DEVISE = {"XOF": "F", "NGN": "₦"}


def normaliser_promotion(texte):
    """'20%' -> '-20 %' ; '10 000 F de réduction' -> '-10000 F' ;
    '10 000 naira de réduction' -> '-10000 ₦'"""
    pct = normaliser_pourcentage(texte)
    if pct:
        return pct
    prix = normaliser_prix(texte, champ="promotion")
    if not prix:
        return None
    symbole = SYMBOLE_DEVISE.get(detecter_devise(texte), "F")
    return f"-{prix} {symbole}"


# --------------------------------------------------------------------------- #
# Dates et périodes
# --------------------------------------------------------------------------- #
MOTIF_JOUR_NOMME = r"\b(" + "|".join(JOURS) + r"|demain|aujourd'hui|week-?end)\b"
# Une période : « du <début> au <fin> ». 'jusqu'au' marque seulement une fin.
MOTIF_PERIODE = r"\bdu\s+(.{1,40}?)\s+au\s+(.{1,40}?)(?=[,.;]|$)"


def _date_existe(jour, mois):
    """2024 est bissextile : le 29 février est accepté, le 30 refusé."""
    return 1 <= mois <= 12 and 1 <= jour <= calendar.monthrange(2024, mois)[1]


def extraire_dates(texte, mois_par_defaut=None):
    """'samedi', 'demain', 'ce week-end', '15 octobre', '15/10' -> liste dans
    l'ordre du texte. Dans une période, un jour sans mois prend le mois de la
    deuxième date : 'du 15 au 20 octobre' -> ['15 octobre', '20 octobre'].
    """
    t = sans_accent(texte)
    trouves = []

    for m in re.finditer(MOTIF_JOUR_NOMME, t):
        mot = m.group(1)
        trouves.append((m.start(), "week-end" if mot.startswith("week") else mot))

    # Positions déjà prises par une date « jour + mois », pour ne pas compter
    # deux fois le même nombre.
    positions_avec_mois = []
    for m in re.finditer(r"\b(\d{1,2})(?:er)?\s+(" + "|".join(MOIS_SA) + r")\b", t):
        positions_avec_mois.append((m.start(), m.end()))
        trouves.append((m.start(), (int(m.group(1)), MOIS_SA.index(m.group(2)) + 1)))

    for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})\b", t):
        positions_avec_mois.append((m.start(), m.end()))
        trouves.append((m.start(), (int(m.group(1)), int(m.group(2)))))

    # Jour nu ('du 15 au 20 octobre' : le 15). On lui donne le mois de la date
    # suivante dans le texte, sinon le mois fourni par l'appelant.
    mois_suivants = sorted((debut, mois) for debut, mois in
                           [(d, v[1]) for d, v in trouves if isinstance(v, tuple)])
    for m in re.finditer(r"\b(\d{1,2})(?:er)?\b", t):
        if any(d <= m.start() < f for d, f in positions_avec_mois):
            continue
        mois = next((mo for d, mo in mois_suivants if d > m.start()), mois_par_defaut)
        if mois:
            trouves.append((m.start(), (int(m.group(1)), mois)))

    dates = []
    for _, v in sorted(trouves, key=lambda x: x[0]):
        if isinstance(v, str):
            dates.append(v)
        elif _date_existe(v[0], v[1]):          # 30 février -> refusé
            dates.append(f"{v[0]} {MOIS[v[1] - 1]}")
    return dates


def extraire_periode(texte):
    """'du 15 au 20 octobre' -> ('15 octobre', '20 octobre') ;
    'du vendredi au dimanche' -> ('vendredi', 'dimanche') ;
    'samedi' -> ('samedi', None)"""
    m = re.search(MOTIF_PERIODE, sans_accent(texte))
    if m:
        # Le mois de la fin ('20 octobre') sert de défaut au début ('15').
        fins = extraire_dates(m.group(2))
        mois_fin = None
        for mot_mois in MOIS_SA:
            if re.search(r"\b" + mot_mois + r"\b", m.group(2)):
                mois_fin = MOIS_SA.index(mot_mois) + 1
                break
        debuts = extraire_dates(m.group(1), mois_par_defaut=mois_fin)
        if debuts and fins:
            return debuts[0], fins[0]
        # Une seule borne valide : on garde ce qui est sûr, pas plus.
        if debuts:
            return debuts[0], None
        if fins:
            return fins[0], None

    dates = extraire_dates(texte)
    return (dates[0] if dates else None), None


def normaliser_date(texte):
    """Renvoie la date de DÉBUT. Dans une période, ce n'est pas la dernière
    date du texte : 'du 15 au 20 octobre' -> '15 octobre'."""
    return extraire_periode(texte)[0]


# --------------------------------------------------------------------------- #
# Langue
# --------------------------------------------------------------------------- #
ALIAS_LANGUES = {"yoruba": "yoruba", "yorouba": "yoruba", "hausa": "hausa",
                 "haoussa": "hausa", "francais": "francais", "fr": "francais"}


def normaliser_langue(texte):
    """'Yorùbá' -> 'yoruba', 'Français' -> 'francais'"""
    return ALIAS_LANGUES.get(sans_accent(texte).strip())


# --------------------------------------------------------------------------- #
# Brief complet
# --------------------------------------------------------------------------- #
NORMALISEURS = {"phone": normaliser_telephone, "promotion": normaliser_promotion,
                "price": normaliser_prix, "start_date": normaliser_date,
                "end_date": normaliser_date, "language": normaliser_langue}


def normaliser_brief(brief):
    """Met chaque champ sous sa forme standard. Si impossible, on garde la valeur
    telle quelle : c'est la validation qui la refusera."""
    propre = dict(brief)
    pays = detecter_pays(brief.get("location"))

    for champ, fonction in NORMALISEURS.items():
        if not brief.get(champ):
            continue
        if champ == "phone":
            propre[champ] = fonction(brief[champ], pays=pays) or brief[champ]
        elif champ == "price":
            propre[champ] = fonction(brief[champ], champ=champ) or brief[champ]
        else:
            propre[champ] = fonction(brief[champ]) or brief[champ]

    # Devise : déduite du prix ou de la réduction, jamais inventée. On ne touche
    # pas à une devise déjà renseignée.
    if not propre.get("currency"):
        devise = next((d for d in (detecter_devise(brief.get("price") or ""),
                                   detecter_devise(brief.get("promotion") or "")) if d), None)
        if devise:
            propre["currency"] = devise

    # Période : « du 15 au 20 octobre » dans start_date remplit aussi end_date,
    # sans écraser une date de fin déjà donnée.
    if brief.get("start_date"):
        debut, fin = extraire_periode(brief["start_date"])
        if debut:
            propre["start_date"] = debut
        if fin and not brief.get("end_date"):
            propre["end_date"] = fin

    return propre


if __name__ == "__main__":
    print("tel benin  :", [normaliser_telephone(x) for x in ["0197000000", "97 00 00 00", "12345"]])
    print("tel nigeria:", [normaliser_telephone(x) for x in ["+234 803 123 4567", "08031234567"]])
    print("tel niger  :", [normaliser_telephone(x) for x in ["+227 96 12 34 56"]])
    print("prix       :", [normaliser_prix(x) for x in ["5 000 F", "₦5000", "5 mille F", "gratuit"]])
    print("devise     :", [detecter_devise(x) for x in ["5000 F", "5000 naira", "3000"]])
    print("promo      :", [normaliser_promotion(x) for x in ["20 pour cent", "10 000 naira de réduction"]])
    print("periode    :", [extraire_periode(x) for x in ["du 15 au 20 octobre", "du vendredi au dimanche", "samedi"]])
    print("langue     :", [normaliser_langue(x) for x in ["Yorùbá", "Haoussa", "swahili"]])
