"""Chaque annonce d'exemple passe par normaliser -> valider -> feu vert, et on compare à l'attendu."""
import json
from pathlib import Path
import pytest
from kpata.brief import pret_pour_generation
from kpata.normalisation import normaliser_brief
from kpata.validation import valider_brief

FICHIER = Path(__file__).parent.parent / "data" / "briefs" / "briefs_fr.json"
BRIEFS = json.loads(FICHIER.read_text(encoding="utf-8"))


@pytest.mark.parametrize("annonce", BRIEFS, ids=lambda a: f"brief{a['id']}")
def test_annonce(annonce):
    brief = normaliser_brief(annonce["slots"])
    pret = pret_pour_generation(brief) and not valider_brief(brief)
    assert pret == annonce["pret_attendu"], annonce["piege"]
