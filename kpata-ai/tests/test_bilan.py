"""Le script de bilan (tache E) tourne et produit un rapport exploitable."""
import importlib.util
import json
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
SCRIPT = RACINE / "scripts" / "bilan_phase0.py"


def charger_module():
    """Importe le script, qui n'est pas un paquet installe."""
    spec = importlib.util.spec_from_file_location("bilan_phase0", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BILAN = charger_module()
RESULTATS = [BILAN.analyser(a) for a in BILAN.charger()]


def test_le_script_existe():
    assert SCRIPT.exists()


def test_toutes_les_annonces_sont_analysees():
    assert len(RESULTATS) == 150


@pytest.mark.parametrize("resultat", RESULTATS, ids=lambda r: f"{r['fichier']}-{r['id']}")
def test_chaque_analyse_est_complete(resultat):
    for cle in ("id", "langue", "intent", "c", "pret", "pret_attendu", "accord",
                "manquants", "invalides", "echecs_normalisation"):
        assert cle in resultat
    assert 0 <= resultat["c"] <= 1, "le score C doit rester entre 0 et 1"
    assert isinstance(resultat["pret"], bool)


def test_le_moteur_est_d_accord_avec_les_annotations():
    desaccords = [(r["fichier"], r["id"], r["piege"]) for r in RESULTATS if not r["accord"]]
    assert not desaccords, f"desaccords : {desaccords}"


def test_les_echecs_de_normalisation_sont_des_cas_invalides_voulus():
    """Une valeur non normalisee doit correspondre a une annonce refusee expres.
    Si une annonce valide echoue a la normalisation, c'est un vrai bug."""
    surprises = [(r["fichier"], r["id"], r["echecs_normalisation"])
                 for r in RESULTATS if r["echecs_normalisation"] and r["pret_attendu"]]
    assert not surprises, f"normalisation en echec sur des annonces valides : {surprises}"


def test_le_rapport_est_ecrit_et_contient_les_sections_demandees(tmp_path, monkeypatch):
    rapport = tmp_path / "bilan_phase0.md"
    monkeypatch.setattr(BILAN, "RAPPORT", rapport)
    BILAN.ecrire_rapport(RESULTATS)
    texte = rapport.read_text(encoding="utf-8")
    for section in ["Nombre d'annonces", "Feu vert", "Champs qui manquent",
                    "Valeurs que la normalisation n'a pas trait",
                    "Répartition des scores", "Annotation",
                    "Générateur de texte", "Ce qui reste à faire"]:
        assert section in texte, f"section manquante : {section}"


def test_la_section_du_generateur_reste_vide_pour_eudes(tmp_path, monkeypatch):
    """Le generateur de texte n'est pas encore pret : la section est reservee."""
    rapport = tmp_path / "bilan.md"
    monkeypatch.setattr(BILAN, "RAPPORT", rapport)
    BILAN.ecrire_rapport(RESULTATS)
    assert "Section réservée" in rapport.read_text(encoding="utf-8")


def test_le_rapport_du_depot_est_a_jour():
    """Le rapport versionne doit correspondre aux donnees actuelles."""
    publie = RACINE / "docs" / "bilan_phase0.md"
    assert publie.exists(), "lancer python scripts/bilan_phase0.py"
    texte = publie.read_text(encoding="utf-8")
    assert f"**{len(RESULTATS)} annonces analysées**" in texte, (
        "le rapport n'est plus a jour : relancer scripts/bilan_phase0.py"
    )


# --------------------------------------------------------------------------- #
# Sources automatiques dans le bilan (tache E, D-010)
# --------------------------------------------------------------------------- #
def test_le_bilan_ignore_les_fichiers_qui_ne_sont_pas_des_annonces():
    """rejets_traduction.json vit dans data/briefs/ mais n'est pas un lot
    d'annonces : il ne doit pas entrer dans les comptages."""
    assert "rejets_traduction.json" in BILAN.PAS_DES_ANNONCES
    fichiers = {r["fichier"] for r in RESULTATS}
    assert not (fichiers & BILAN.PAS_DES_ANNONCES)


def test_le_bilan_croise_langue_et_origine(tmp_path, monkeypatch):
    """D-010 exige de pouvoir lire les volumes par langue ET par source."""
    rapport = tmp_path / "bilan.md"
    monkeypatch.setattr(BILAN, "RAPPORT", rapport)
    BILAN.ecrire_rapport(RESULTATS)
    texte = rapport.read_text(encoding="utf-8")
    assert "Par langue et par origine" in texte


def test_la_section_traduction_auto_ne_plante_pas_sans_donnees():
    """Avant le premier lancement de traduire_auto.py, la section doit le dire
    au lieu d'inventer des chiffres."""
    parties = BILAN._section_traduction_auto()
    assert parties, "la section doit toujours exister"
    assert any("Traduction automatique" in p for p in parties)
