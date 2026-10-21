"""Le code et docs/schema_annonce.md doivent rester alignes (tache B).

Ce test lit le tableau des champs du document et le compare aux constantes de
brief.py. Si l'un des deux change sans l'autre, il echoue. Lecture volontairement
simple : pas de dependance, uniquement la bibliotheque standard.
"""
import re
from pathlib import Path

import pytest

from kpata.brief import CHAMPS, INTENTS, MEDIAS, OBLIGATOIRES, POIDS, SEUIL, TONS

DOC = Path(__file__).parent.parent / "docs" / "schema_annonce.md"
TEXTE = DOC.read_text(encoding="utf-8")


def lignes_du_tableau_des_champs():
    """Les lignes '| `champ` | definition | forme | poids | obligatoire |'."""
    lignes = []
    for ligne in TEXTE.splitlines():
        cellules = [c.strip() for c in ligne.split("|")[1:-1]]
        if len(cellules) == 5 and cellules[0].startswith("`"):
            nom = cellules[0].strip("`")
            lignes.append((nom, cellules[3]))
    return lignes


def test_le_document_existe():
    assert DOC.exists(), "docs/schema_annonce.md est le document de reference"


def test_le_tableau_des_champs_est_complet():
    noms = [nom for nom, _ in lignes_du_tableau_des_champs()]
    assert set(noms) == set(CHAMPS), (
        f"document seulement : {set(noms) - set(CHAMPS)} ; "
        f"code seulement : {set(CHAMPS) - set(noms)}"
    )


@pytest.mark.parametrize("nom, poids_doc", lignes_du_tableau_des_champs())
def test_chaque_poids_du_document_correspond_au_code(nom, poids_doc):
    if poids_doc == "—":                      # language et intent : pas de poids
        assert nom not in POIDS, f"{nom} ne doit pas avoir de poids"
    else:
        assert POIDS[nom] == int(poids_doc), f"poids de {nom}"


def test_aucun_poids_orphelin():
    """POIDS ne doit pas peser un champ absent du schema."""
    assert set(POIDS) <= set(CHAMPS)


def test_les_sept_intentions_sont_documentees():
    """Le cahier des charges §7.1 fixe exactement sept intentions."""
    assert len(INTENTS) == 7
    for intent in INTENTS:
        assert f"`{intent}`" in TEXTE, f"{intent} n'est pas documentee"


def test_chaque_intention_a_des_champs_obligatoires():
    assert set(OBLIGATOIRES) == set(INTENTS)


def test_tons_et_medias_sont_documentes():
    for valeur in TONS + MEDIAS:
        assert f"`{valeur}`" in TEXTE, f"{valeur} n'est pas documente"


def test_le_seuil_en_vigueur_est_annonce_dans_le_document():
    assert str(SEUIL).replace(".", ",") in TEXTE, "le seuil en vigueur doit figurer au §5"


def test_telephone_et_lieu_obligatoires_pour_toutes_les_intentions():
    """Cahier §4 : le systeme ne doit jamais inventer un telephone manquant."""
    for intent, items in OBLIGATOIRES.items():
        plats = [c for i in items for c in ((i,) if isinstance(i, str) else i)]
        assert "phone" in plats, f"{intent} doit exiger un telephone"
        assert "location" in plats, f"{intent} doit exiger un lieu"
