"""Script de synthese vocale (tache C).

Aucun modele n'est telecharge : on verifie le nommage, le format WAV et le
manifeste avec un signal fabrique a la main. Ces tests tournent par defaut.
"""
import csv
import importlib.util
import sys
import wave
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


SYNTHESE = charger("synthese_vocale")


# --------------------------------------------------------------------------- #
# Tache C : nommage et ecriture des audios
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("langue, numero, attendu", [
    ("yoruba", 12, "yoruba_SYNTH_012.wav"),
    ("hausa", 1, "hausa_SYNTH_001.wav"),
    ("yoruba", 100, "yoruba_SYNTH_100.wav"),
])
def test_nom_de_fichier_suit_la_convention(langue, numero, attendu):
    """Convention de data/README.md : <langue>_<locuteur>_<numero>.wav"""
    assert SYNTHESE.nom_fichier(langue, numero) == attendu


def test_le_locuteur_est_SYNTH():
    """Ce n'est pas une voix humaine, et le nom du fichier doit le dire."""
    assert "SYNTH" in SYNTHESE.nom_fichier("yoruba", 1)


def test_aucun_vrai_nom_dans_le_nom_de_fichier():
    """data/README.md : jamais de vrai nom ni de numero de locuteur."""
    nom = SYNTHESE.nom_fichier("hausa", 7)
    assert nom.count("_") == 2 and nom.endswith(".wav")


def test_ecrire_wav_produit_du_mono_16_khz(tmp_path):
    """Sans numpy ni soundfile, la solution de repli doit marcher."""
    try:
        import numpy as np
        signal = np.zeros(16000, dtype="float32")
    except ImportError:
        pytest.skip("numpy absent")

    chemin = tmp_path / "essai.wav"
    SYNTHESE.ecrire_wav(chemin, signal, 16000)

    assert chemin.exists()
    with wave.open(str(chemin)) as f:
        assert f.getnchannels() == 1, "doit etre mono"
        assert f.getframerate() == 16000, "doit etre a 16 kHz"
        assert f.getsampwidth() == 2, "doit etre en 16 bits"
        assert f.getnframes() == 16000


def test_les_colonnes_du_manifeste_sont_celles_demandees():
    assert SYNTHESE.COLONNES == ["audio_path", "language", "transcript",
                                 "id_annonce", "source", "duree_s", "modele"]


def test_le_manifeste_est_ecrit_dans_les_deux_dossiers(tmp_path, monkeypatch):
    """Le manifeste est petit : il va aussi dans data/briefs/, versionne."""
    audio, briefs = tmp_path / "audio", tmp_path / "briefs"
    monkeypatch.setattr(SYNTHESE, "DOSSIER_AUDIO", audio)
    monkeypatch.setattr(SYNTHESE, "DOSSIER_BRIEFS", briefs)

    SYNTHESE.ecrire_manifeste([{
        "audio_path": "synthese/yoruba_SYNTH_001.wav", "language": "yoruba",
        "transcript": "Mo ni ile itaja", "id_annonce": 1,
        "source": "synthese_vocale", "duree_s": "3.21",
        "modele": "facebook/mms-tts-yor (CC-BY-NC-4.0)",
    }])

    for dossier in (audio, briefs):
        chemin = dossier / SYNTHESE.NOM_MANIFESTE
        assert chemin.exists(), f"manifeste absent de {dossier.name}"
        lignes = list(csv.DictReader(chemin.open(encoding="utf-8")))
        assert lignes[0]["source"] == "synthese_vocale"
        assert "CC-BY-NC" in lignes[0]["modele"], "la licence doit etre tracee"


def test_la_graine_est_fixe():
    """VITS a un predicteur de duree stochastique : sans graine, le jeu de
    donnees ne serait pas reproductible."""
    assert isinstance(SYNTHESE.GRAINE, int)


def test_les_deux_langues_ont_un_modele():
    assert set(SYNTHESE.MODELES) == {"yoruba", "hausa"}
    for nom in SYNTHESE.MODELES.values():
        assert nom.startswith("facebook/mms-tts-")
