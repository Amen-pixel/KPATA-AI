import pytest
from kpata.normalisation import (normaliser_telephone, normaliser_prix, normaliser_pourcentage,
                                 normaliser_promotion, normaliser_date, normaliser_langue,
                                 normaliser_brief)


@pytest.mark.parametrize("brut, attendu", [
    ("0197000000", "+2290197000000"),
    ("97 00 00 00", "+2290197000000"),
    ("+229 01 97 00 00 00", "+2290197000000"),
    ("00229 97000000", "+2290197000000"),
    ("+229 97 11 22 33", "+2290197112233"),
    ("12345", None),
    ("", None),
])
def test_telephone(brut, attendu):
    assert normaliser_telephone(brut) == attendu


@pytest.mark.parametrize("brut, attendu", [
    ("5 000 F", 5000), ("5000 fcfa", 5000), ("5.000 CFA", 5000), ("gratuit", None), ("150%", None),
])
def test_prix(brut, attendu):
    assert normaliser_prix(brut) == attendu


@pytest.mark.parametrize("brut, attendu", [
    ("20%", "-20 %"), ("-20 %", "-20 %"), ("20 pour cent", "-20 %"), ("150%", None), ("0%", None),
])
def test_pourcentage(brut, attendu):
    assert normaliser_pourcentage(brut) == attendu


@pytest.mark.parametrize("brut, attendu", [
    ("20%", "-20 %"), ("10 000 F de réduction", "-10000 F"), ("-10000 F", "-10000 F"), ("150%", None),
])
def test_promotion(brut, attendu):
    assert normaliser_promotion(brut) == attendu


@pytest.mark.parametrize("brut, attendu", [
    ("vendredi", "vendredi"), ("le 15 octobre", "15 octobre"), ("15/10", "15 octobre"),
    ("1er novembre", "1 novembre"), ("ce week-end", "week-end"), ("demain", "demain"),
    ("29 février", "29 février"), ("30 février", None), ("32 mars", None), ("vendradi", None),
])
def test_date(brut, attendu):
    assert normaliser_date(brut) == attendu


@pytest.mark.parametrize("brut, attendu", [
    ("Yorùbá", "yoruba"), ("Haoussa", "hausa"), ("Français", "francais"), ("swahili", None),
])
def test_langue(brut, attendu):
    assert normaliser_langue(brut) == attendu


def test_normaliser_brief_est_idempotent():
    brut = {"phone": "97 00 00 00", "promotion": "20%", "price": "2 500 F", "start_date": "Vendredi"}
    une_fois = normaliser_brief(brut)
    assert une_fois["phone"] == "+2290197000000"
    assert une_fois["price"] == 2500
    assert normaliser_brief(une_fois) == une_fois


def test_normaliser_brief_garde_ce_qui_est_invalide():
    assert normaliser_brief({"phone": "12345"})["phone"] == "12345"
