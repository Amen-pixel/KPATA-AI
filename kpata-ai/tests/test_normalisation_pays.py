"""Tache A1 : telephones du Benin, du Nigeria et du Niger.

Les locuteurs Yoruba et Hausa sont surtout au Nigeria et au Niger : le code ne
doit plus refuser leurs numeros. Le Benin reste le pays par defaut quand on n'a
aucune indication, pour ne pas changer le comportement existant.
"""
import pytest

from kpata.normalisation import detecter_pays, normaliser_brief, normaliser_telephone

BENIN_10 = "0197000000"
BENIN_8 = "97 00 00 00"
BENIN_ATTENDU = "+229" + BENIN_10

NIGERIA_ATTENDU = "+234" + "8031234567"
NIGER_ATTENDU = "+227" + "96123456"


@pytest.mark.parametrize("brut, attendu", [
    # Nigeria : indicatif +234, 10 chiffres significatifs
    ("+234 803 123 4567", NIGERIA_ATTENDU),
    ("0803 123 4567", NIGERIA_ATTENDU),          # 11 chiffres commencant par 0
    ("00234 803 123 4567", NIGERIA_ATTENDU),
    ("+2348031234567", NIGERIA_ATTENDU),
    # Niger : indicatif +227, 8 chiffres significatifs
    ("+227 96 12 34 56", NIGER_ATTENDU),
    ("00227 96123456", NIGER_ATTENDU),
    # Benin : comportement actuel inchange
    (BENIN_10, BENIN_ATTENDU),
    (BENIN_8, BENIN_ATTENDU),
    ("+229 01 97 00 00 00", BENIN_ATTENDU),
    # Refus
    ("12345", None),
    ("", None),
    ("0803 123 456", None),                      # 10 chiffres commencant par 08 : incomplet
])
def test_telephone_trois_pays(brut, attendu):
    assert normaliser_telephone(brut) == attendu


def test_huit_chiffres_est_benin_par_defaut():
    """Cas ambigu : 8 chiffres sans indicatif. Par defaut, Benin (ancien format)."""
    assert normaliser_telephone(BENIN_8) == BENIN_ATTENDU


def test_huit_chiffres_devient_nigerien_si_le_pays_est_donne():
    assert normaliser_telephone("96 12 34 56", pays="niger") == NIGER_ATTENDU


def test_pays_explicite_nigeria():
    assert normaliser_telephone("803 123 4567", pays="nigeria") == NIGERIA_ATTENDU


@pytest.mark.parametrize("lieu, attendu", [
    ("Niamey", "niger"),
    ("Zinder", "niger"),
    ("quartier Maradi ville", "niger"),
    ("Tahoua", "niger"),
    ("Agadez", "niger"),
    ("Dosso", "niger"),
    ("Abomey-Calavi", None),
    ("Lagos", None),
    (None, None),
])
def test_detecter_pays_depuis_le_lieu(lieu, attendu):
    assert detecter_pays(lieu) == attendu


def test_brief_a_niamey_utilise_le_niger():
    brief = normaliser_brief({"location": "Niamey", "phone": "96 12 34 56"})
    assert brief["phone"] == NIGER_ATTENDU


def test_brief_a_calavi_reste_au_benin():
    brief = normaliser_brief({"location": "Abomey-Calavi", "phone": BENIN_8})
    assert brief["phone"] == BENIN_ATTENDU
