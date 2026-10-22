"""Tache A2 : prix en naira, prix ecrits en lettres, nombre seul dans un champ."""
import pytest

from kpata.normalisation import (detecter_devise, normaliser_brief, normaliser_prix,
                                 normaliser_promotion)


@pytest.mark.parametrize("brut, attendu", [
    # Naira
    ("\u20a65000", 5000),
    ("N5000", 5000),
    ("5000 naira", 5000),
    ("5 000 nairas", 5000),
    # Franc CFA : comportement actuel
    ("5000 F", 5000),
    ("5000 FCFA", 5000),
    ("5 000 CFA", 5000),
    # Ecrit en lettres
    ("5 mille F", 5000),
    ("5 mille", 5000),
    ("2 mille naira", 2000),
    # Refus
    ("gratuit", None),
    ("150%", None),
])
def test_prix(brut, attendu):
    assert normaliser_prix(brut) == attendu


def test_prix_reste_un_entier():
    assert isinstance(normaliser_prix("5 000 nairas"), int)


@pytest.mark.parametrize("brut, attendu", [
    ("5000 F", "XOF"),
    ("5 000 FCFA", "XOF"),
    ("5.000 CFA", "XOF"),
    ("3000 francs", "XOF"),
    ("\u20a65000", "NGN"),
    ("N5000", "NGN"),
    ("5000 naira", "NGN"),
    ("5 000 nairas", "NGN"),
    ("3000", None),
    ("gratuit", None),
])
def test_detecter_devise(brut, attendu):
    assert detecter_devise(brut) == attendu


@pytest.mark.parametrize("champ", ["price", "promotion"])
def test_nombre_seul_accepte_dans_un_champ(champ):
    """Un nombre seul est un prix seulement si la valeur vient du champ price ou promotion."""
    assert normaliser_prix("3000", champ=champ) == 3000


def test_nombre_seul_refuse_dans_un_texte_libre():
    """Dans un texte libre, un nombre seul peut etre un numero de telephone : on refuse."""
    assert normaliser_prix("3000") is None
    assert normaliser_prix("appelez le 3000", champ="price") is None


def test_nombre_seul_sans_devise():
    assert detecter_devise("3000") is None


@pytest.mark.parametrize("brut, attendu", [
    ("20%", "-20 %"),
    ("10 000 F de r\u00e9duction", "-10000 F"),
    ("-10000 F", "-10000 F"),
    ("10 000 naira de r\u00e9duction", "-10000 \u20a6"),
    ("-10000 \u20a6", "-10000 \u20a6"),
    ("150%", None),
])
def test_promotion_garde_la_devise(brut, attendu):
    assert normaliser_promotion(brut) == attendu


def test_brief_remplit_la_devise():
    brief = normaliser_brief({"price": "5000 naira", "location": "Kano"})
    assert brief["price"] == 5000
    assert brief["currency"] == "NGN"


def test_brief_devise_xof():
    brief = normaliser_brief({"price": "2 500 F"})
    assert brief["currency"] == "XOF"


def test_brief_sans_devise_najoute_rien():
    """Pas de devise detectee : on n'invente pas, le champ reste absent."""
    assert "currency" not in normaliser_brief({"price": 3000})


def test_brief_najoute_pas_une_devise_par_dessus_une_autre():
    brief = normaliser_brief({"price": "5000 F", "currency": "NGN"})
    assert brief["currency"] == "NGN"


@pytest.mark.parametrize("texte", ["rendez-vous en 2026", "bref 20 modèles", "bien 5 modèles"])
def test_lettre_au_bout_d_un_mot_n_est_pas_un_symbole_de_devise(texte):
    assert normaliser_prix(texte) is None
    assert detecter_devise(texte) is None


@pytest.mark.parametrize("texte, prix, devise", [
    ("N5000", 5000, "NGN"), ("N 5000", 5000, "NGN"), ("₦5000", 5000, "NGN"),
    ("f 5000", 5000, "XOF"), ("chaussures N5000", 5000, "NGN"),
])
def test_vrais_symboles_restent_reconnus(texte, prix, devise):
    assert normaliser_prix(texte) == prix
    assert detecter_devise(texte) == devise
