"""Contrôle de fidélité d'une traduction automatique (D-010).

Code pur : aucun modèle, aucune dépendance lourde, seulement la bibliothèque
standard et le reste du paquet `kpata`. C'est ce qui le rend testable.

Principe : on ne fait pas confiance à la traduction, on la vérifie. Une annonce
dont une information critique a changé pendant la traduction est **rejetée**,
jamais corrigée à la main. La règle d'or du cahier des charges (§7.2) interdit
qu'un prix, une date, un numéro ou un lieu faux arrive sur une affiche.
"""
import re
import unicodedata

from .normalisation import (extraire_dates, normaliser_brief, normaliser_prix,
                            sans_accent)

# Champs dont la valeur normalisée doit survivre à l'aller-retour de traduction.
CHAMPS_CRITIQUES = ["phone", "price", "promotion", "start_date", "end_date"]

# Champs qui contiennent un nom propre : ils doivent apparaître tels quels dans
# la traduction, car un nom propre ne se traduit pas.
CHAMPS_NOMS_PROPRES = ["location", "business_name"]


def chiffres_seuls(texte):
    """'+234 803 111 2233' -> '2348031112233'. Pour comparer des nombres sans
    se soucier des espaces, tirets ou points."""
    return re.sub(r"\D", "", str(texte))


def nombres_du_texte(texte):
    """Tous les groupes de chiffres d'un texte, sans la ponctuation interne.
    '20% vendredi, 5 000 F' -> ['20', '5000'] (les espaces dans un nombre sont
    recollés, car '5 000' est un seul nombre)."""
    recolle = re.sub(r"(?<=\d)[\s.](?=\d)", "", str(texte))
    return re.findall(r"\d+", recolle)


def nombres_critiques(annonce):
    """Les nombres que la traduction doit absolument préserver.

    Renvoie une liste de couples (étiquette, chiffres), par exemple
    [('téléphone', '2348031112233'), ('pourcentage', '20')].
    """
    slots = annonce.get("slots", {})
    attendus = []

    if slots.get("phone"):
        attendus.append(("téléphone", chiffres_seuls(slots["phone"])))

    if slots.get("price"):
        prix = normaliser_prix(slots["price"], champ="price")
        if prix:
            attendus.append(("prix", str(prix)))

    promo = slots.get("promotion")
    if promo:
        pct = re.search(r"(\d{1,3})\s*(?:%|pour\s?cent)", sans_accent(promo))
        if pct:
            attendus.append(("pourcentage", pct.group(1)))
        else:
            montant = normaliser_prix(promo, champ="promotion")
            if montant:
                attendus.append(("réduction", str(montant)))

    # Jour du mois : '15 octobre' -> '15'. Un jour nommé ('vendredi') n'a pas de
    # chiffre à vérifier ici.
    for champ in ("start_date", "end_date"):
        for date in extraire_dates(slots.get(champ) or ""):
            jour = re.match(r"(\d{1,2})\b", date)
            if jour:
                attendus.append((f"jour ({champ})", jour.group(1)))

    # Dédoublonnage en gardant l'ordre, pour ne pas répéter une raison.
    vus, uniques = set(), []
    for etiquette, valeur in attendus:
        if valeur and valeur not in vus:
            vus.add(valeur)
            uniques.append((etiquette, valeur))
    return uniques


def _normalise_pour_comparer(texte):
    """Minuscules, sans accents, sans ponctuation : pour chercher un nom propre
    sans être gêné par la casse ou un tiret."""
    base = sans_accent(texte)
    return re.sub(r"[^\w\s]", " ", base)


def nom_propre_present(nom, traduction):
    """Le nom propre apparaît-il dans la traduction ?

    On accepte qu'il soit découpé différemment ('Abomey-Calavi' contre
    'Abomey Calavi'), mais chaque mot significatif doit être là. Les mots très
    courts (1 ou 2 lettres) sont ignorés : ce sont des articles.
    """
    cible = _normalise_pour_comparer(traduction)
    mots = [m for m in _normalise_pour_comparer(nom).split() if len(m) > 2]
    if not mots:                          # nom trop court pour être vérifiable
        return True
    return all(re.search(r"\b" + re.escape(m) + r"\b", cible) for m in mots)


def controler(annonce, traduction, retro_traduction):
    """Une traduction est-elle fidèle ? Renvoie (ok, raisons).

    `ok` est vrai seulement si TOUTES les conditions sont remplies. Sinon,
    `raisons` liste en français ce qui a échoué, pour pouvoir trancher plus tard
    sans relancer le modèle.
    """
    raisons = []
    traduction = (traduction or "").strip()
    retro = (retro_traduction or "").strip()
    source = (annonce.get("transcript_source_fr") or "").strip()

    # 1. La traduction existe-t-elle vraiment ?
    if not traduction:
        return False, ["traduction vide"]

    if _normalise_pour_comparer(traduction) == _normalise_pour_comparer(source):
        raisons.append("traduction identique au texte français")

    # 2. Chaque nombre critique apparaît-il à l'identique ?
    presents = nombres_du_texte(traduction)
    colles = chiffres_seuls(traduction)
    for etiquette, attendu in nombres_critiques(annonce):
        # Soit le nombre est isolé, soit il est noyé dans une suite de chiffres
        # (un téléphone peut être écrit sans espaces).
        if attendu not in presents and attendu not in colles:
            raisons.append(f"{etiquette} {attendu} absent de la traduction")

    # 3. Les noms propres sont-ils conservés ?
    for champ in CHAMPS_NOMS_PROPRES:
        valeur = annonce.get("slots", {}).get(champ)
        if valeur and not nom_propre_present(valeur, traduction):
            etiquette = "lieu" if champ == "location" else "nom du commerce"
            raisons.append(f"{etiquette} « {valeur} » absent ou traduit")

    # 4. La retraduction redonne-t-elle les mêmes valeurs normalisées ?
    if not retro:
        raisons.append("retro-traduction vide")
    else:
        attendu = normaliser_brief(annonce.get("slots", {}))
        # On relit les champs critiques depuis le TEXTE retraduit, pas depuis
        # les slots : c'est tout l'intérêt du contrôle.
        obtenu = normaliser_brief({**annonce.get("slots", {}),
                                   **_relire_depuis_texte(retro, attendu)})
        for champ in CHAMPS_CRITIQUES:
            if attendu.get(champ) and obtenu.get(champ) != attendu.get(champ):
                raisons.append(
                    f"{champ} change apres retro-traduction : "
                    f"{attendu.get(champ)} -> {obtenu.get(champ)}")

    return not raisons, raisons


def _relire_depuis_texte(texte, attendu):
    """Relit les champs critiques dans un texte libre, pour les comparer aux
    valeurs attendues. On ne relit que ce qui est vérifiable dans du texte :
    les nombres et les dates."""
    relu = {}
    chiffres = chiffres_seuls(texte)
    nombres = nombres_du_texte(texte)

    if attendu.get("phone"):
        # Le numéro attendu est sous forme '+229...' : on compare les chiffres.
        vise = chiffres_seuls(attendu["phone"])
        relu["phone"] = attendu["phone"] if vise in chiffres else None

    if attendu.get("price"):
        vise = str(attendu["price"])
        relu["price"] = attendu["price"] if vise in nombres else None

    if attendu.get("promotion"):
        vise = chiffres_seuls(attendu["promotion"])
        relu["promotion"] = attendu["promotion"] if vise in nombres else None

    for champ in ("start_date", "end_date"):
        if attendu.get(champ):
            dates = extraire_dates(texte)
            relu[champ] = attendu[champ] if attendu[champ] in dates else None

    return relu


def resumer(rejets):
    """Les raisons de rejet les plus fréquentes. Pour le rapport."""
    from collections import Counter
    # On enlève les valeurs des messages pour regrouper les raisons de même
    # nature : 'prix 5000 absent' et 'prix 300 absent' comptent ensemble.
    familles = Counter()
    for rejet in rejets:
        for raison in rejet.get("raisons", []):
            famille = re.sub(r"\d+", "N", raison)
            famille = re.sub(r"«.*?»", "«…»", famille)
            familles[famille] += 1
    return familles.most_common()
