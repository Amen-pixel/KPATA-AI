"""Protocole de verification humaine d'un echantillon (tache D).

Aucun modele n'est telecharge : le tirage et la lecture des resultats sont
testes avec de fausses annonces et de faux CSV. Ces tests tournent par defaut.
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent


def charger(nom):
    """Importe un script de scripts/, qui n'est pas un paquet installe."""
    chemin = RACINE / "scripts" / f"{nom}.py"
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


ECHANTILLON = charger("echantillon_verification")
RESULTATS = charger("resultats_verification")


# --------------------------------------------------------------------------- #
# Tirage de l'echantillon
# --------------------------------------------------------------------------- #
def fausses_annonces(nombre):
    return [{
        "id": i,
        "transcript": f"traduction {i}",
        "texte_source_fr": f"texte francais {i}",
        "slots": {"language": "yoruba", "intent": "promotion"},
        "pret_attendu": True, "piege": "",
        "source": "traduit_auto",
    } for i in range(1, nombre + 1)]


@pytest.fixture
def briefs_bidons(tmp_path, monkeypatch):
    monkeypatch.setattr(ECHANTILLON, "DOSSIER_BRIEFS", tmp_path)
    for langue in ("yoruba", "hausa"):
        (tmp_path / f"briefs_{langue}_auto.json").write_text(
            json.dumps(fausses_annonces(40), ensure_ascii=False), encoding="utf-8")
    return tmp_path


def test_le_tirage_donne_vingt_annonces(briefs_bidons):
    assert len(ECHANTILLON.tirer("yoruba")) == 20


def test_le_tirage_est_reproductible(briefs_bidons):
    """Meme graine, meme tirage : deux relecteurs peuvent etre compares."""
    premier = [a["id"] for a in ECHANTILLON.tirer("yoruba")]
    second = [a["id"] for a in ECHANTILLON.tirer("yoruba")]
    assert premier == second


def test_une_graine_differente_donne_un_autre_tirage(briefs_bidons):
    a = [x["id"] for x in ECHANTILLON.tirer("yoruba", graine=1)]
    b = [x["id"] for x in ECHANTILLON.tirer("yoruba", graine=2)]
    assert a != b


def test_les_deux_langues_ont_des_tirages_differents(briefs_bidons):
    """La graine inclut la langue : les deux echantillons ne sont pas identiques."""
    yor = [a["id"] for a in ECHANTILLON.tirer("yoruba")]
    hau = [a["id"] for a in ECHANTILLON.tirer("hausa")]
    assert yor != hau


def test_le_tirage_ne_depasse_pas_le_stock(briefs_bidons, tmp_path):
    (tmp_path / "briefs_yoruba_auto.json").write_text(
        json.dumps(fausses_annonces(5)), encoding="utf-8")
    assert len(ECHANTILLON.tirer("yoruba")) == 5


def test_fichier_absent_ne_fait_pas_planter(tmp_path, monkeypatch):
    monkeypatch.setattr(ECHANTILLON, "DOSSIER_BRIEFS", tmp_path)
    assert ECHANTILLON.tirer("yoruba") == []


def test_l_export_laisse_les_colonnes_du_relecteur_vides(briefs_bidons, tmp_path,
                                                         monkeypatch):
    monkeypatch.setattr(ECHANTILLON, "DOSSIER_SORTIE", tmp_path / "verif")
    chemin = ECHANTILLON.exporter("yoruba", ECHANTILLON.tirer("yoruba"))
    lignes = list(csv.DictReader(chemin.open(encoding="utf-8")))

    assert len(lignes) == 20
    for ligne in lignes:
        assert ligne["texte_fr"] and ligne["traduction"], "le relecteur doit voir les deux textes"
        for colonne in ("sens_correct (oui/non)", "infos_critiques_correctes (oui/non)",
                        "naturel (1-5)", "commentaire"):
            assert ligne[colonne] == "", f"{colonne} doit etre vide"


def test_les_colonnes_sont_celles_demandees():
    assert ECHANTILLON.COLONNES == [
        "id", "texte_fr", "traduction", "sens_correct (oui/non)",
        "infos_critiques_correctes (oui/non)", "naturel (1-5)", "commentaire"]


# --------------------------------------------------------------------------- #
# Tache D : lecture des resultats
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("valeur, attendu", [
    ("oui", True), ("OUI", True), ("o", True), ("yes", True), ("1", True),
    ("non", False), ("NON", False), ("n", False), ("no", False), ("0", False),
    ("", None), ("peut-etre", None), (None, None),
])
def test_lecture_oui_non(valeur, attendu):
    assert RESULTATS.oui_non(valeur) is attendu


@pytest.mark.parametrize("valeur, attendu", [
    ("5", 5.0), ("1", 1.0), ("3,5", 3.5), ("3.5", 3.5),
    ("0", None), ("6", None), ("", None), ("bien", None),
])
def test_lecture_de_la_note(valeur, attendu):
    assert RESULTATS.note(valeur) == attendu


def test_analyse_calcule_les_trois_mesures():
    lignes = [
        {"id": "1", "sens_correct (oui/non)": "oui",
         "infos_critiques_correctes (oui/non)": "oui", "naturel (1-5)": "4"},
        {"id": "2", "sens_correct (oui/non)": "non",
         "infos_critiques_correctes (oui/non)": "oui", "naturel (1-5)": "2"},
        {"id": "3", "sens_correct (oui/non)": "oui",
         "infos_critiques_correctes (oui/non)": "non", "naturel (1-5)": "3"},
    ]
    r = RESULTATS.analyser(lignes)
    assert r["pct_sens"] == pytest.approx(66.7, abs=0.1)
    assert r["pct_infos"] == pytest.approx(66.7, abs=0.1)
    assert r["naturel_moyen"] == pytest.approx(3.0)
    assert r["echecs_critiques"] == ["3"]


def test_les_cases_vides_ne_comptent_pas():
    lignes = [
        {"id": "1", "sens_correct (oui/non)": "oui",
         "infos_critiques_correctes (oui/non)": "", "naturel (1-5)": ""},
        {"id": "2", "sens_correct (oui/non)": "",
         "infos_critiques_correctes (oui/non)": "", "naturel (1-5)": ""},
    ]
    r = RESULTATS.analyser(lignes)
    assert r["pct_sens"] == 100.0 and r["remplies_sens"] == 1
    assert r["pct_infos"] is None and r["naturel_moyen"] is None


def test_un_echantillon_vide_ne_fait_pas_planter():
    r = RESULTATS.analyser([])
    assert r["pct_sens"] is None and r["echecs_critiques"] == []


def test_les_consignes_du_relecteur_existent_en_deux_langues():
    chemin = RACINE / "docs" / "verification" / "consignes_relecteur.md"
    assert chemin.exists()
    texte = chemin.read_text(encoding="utf-8")
    assert "sens_correct" in texte and "infos_critiques_correctes" in texte
    assert "naturel" in texte
    assert "English" in texte, "les consignes doivent aussi etre en anglais"
    assert "ne corrigez pas" in texte.lower(), "le relecteur ne doit pas corriger"
