"""Tache A3 : les periodes de dates.

« du 15 au 20 octobre » donnait « 20 octobre » comme date de debut : une
information fausse. La regle d'or interdit ce genre d'erreur.
"""
import pytest

from kpata.normalisation import (extraire_dates, extraire_periode, normaliser_brief,
                                 normaliser_date)


@pytest.mark.parametrize("brut, attendu", [
    ("du 15 au 20 octobre", ("15 octobre", "20 octobre")),
    ("du vendredi au dimanche", ("vendredi", "dimanche")),
    ("samedi", ("samedi", None)),
    ("du 28 octobre au 3 novembre", ("28 octobre", "3 novembre")),
    ("du 1er au 5 mars", ("1 mars", "5 mars")),
    ("", (None, None)),
    ("gratuit", (None, None)),
])
def test_extraire_periode(brut, attendu):
    assert extraire_periode(brut) == attendu


def test_jour_sans_mois_prend_le_mois_de_la_deuxieme_date():
    assert extraire_dates("du 15 au 20 octobre") == ["15 octobre", "20 octobre"]


def test_periode_a_cheval_sur_deux_mois():
    assert extraire_dates("du 28 octobre au 3 novembre") == ["28 octobre", "3 novembre"]


def test_normaliser_date_ne_renvoie_plus_la_fin_comme_debut():
    """Le bug : « du 15 au 20 octobre » renvoyait « 20 octobre »."""
    assert normaliser_date("du 15 au 20 octobre") == "15 octobre"


def test_brief_remplit_start_et_end_depuis_une_periode():
    brief = normaliser_brief({"start_date": "du 15 au 20 octobre"})
    assert brief["start_date"] == "15 octobre"
    assert brief["end_date"] == "20 octobre"


def test_brief_necrase_pas_une_fin_deja_renseignee():
    brief = normaliser_brief({"start_date": "du 15 au 20 octobre", "end_date": "25 octobre"})
    assert brief["start_date"] == "15 octobre"
    assert brief["end_date"] == "25 octobre"


def test_brief_sans_periode_est_inchange():
    brief = normaliser_brief({"start_date": "vendredi", "end_date": "samedi"})
    assert (brief["start_date"], brief["end_date"]) == ("vendredi", "samedi")


def test_brief_jour_seul_najoute_pas_de_fin():
    """On n'invente pas une date de fin que le commercant n'a pas donnee."""
    assert normaliser_brief({"start_date": "samedi"}).get("end_date") is None


def test_periode_invalide_est_refusee():
    """30 fevrier n'existe pas : on ne garde pas une date fausse."""
    assert extraire_periode("du 28 au 30 f\u00e9vrier") == ("28 f\u00e9vrier", None)
