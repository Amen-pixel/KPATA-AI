"""Les annonces respectent le guide d'annotation et les objectifs de la tache D.

Objectif de l'equipe : 150 annonces, 50 par langue. Le francais est annote et
teste ; le Yoruba et le Hausa sont prepares en attente d'un locuteur natif.
"""
import json
from collections import Counter
from pathlib import Path

import pytest

from kpata.brief import INTENTS, pret_pour_generation
from kpata.normalisation import normaliser_brief
from kpata.validation import valider_brief

DOSSIER = Path(__file__).parent.parent / "data" / "briefs"
FR = json.loads((DOSSIER / "briefs_fr.json").read_text(encoding="utf-8"))
A_TRADUIRE = {
    langue: json.loads((DOSSIER / f"a_traduire_{langue}.json").read_text(encoding="utf-8"))
    for langue in ("yoruba", "hausa")
}
TOUT = FR + A_TRADUIRE["yoruba"] + A_TRADUIRE["hausa"]
SOURCES = {"ecrit_equipe", "natif", "traduit_verifie", "traduit_non_verifie", "a_traduire"}


# --------------------------------------------------------------------------- #
# Objectifs de volume
# --------------------------------------------------------------------------- #
def test_cinquante_annonces_en_francais():
    assert len(FR) == 50


@pytest.mark.parametrize("langue", ["yoruba", "hausa"])
def test_cinquante_annonces_par_langue_a_traduire(langue):
    assert len(A_TRADUIRE[langue]) == 50


def test_cent_cinquante_annonces_au_total():
    """Le cahier des charges demande 100 a 200 annonces ; l'objectif est 150."""
    assert len(TOUT) == 150
    assert 100 <= len(TOUT) <= 200


# --------------------------------------------------------------------------- #
# Couverture et equilibre
# --------------------------------------------------------------------------- #
def test_les_sept_intentions_sont_presentes_cinq_fois_en_francais():
    compte = Counter(a["slots"]["intent"] for a in FR)
    assert set(compte) == set(INTENTS)
    rares = {i: n for i, n in compte.items() if n < 5}
    assert not rares, f"intentions sous-representees : {rares}"


@pytest.mark.parametrize("langue", ["yoruba", "hausa"])
def test_les_sept_intentions_sont_presentes_dans_chaque_langue(langue):
    compte = Counter(a["slots"]["intent"] for a in A_TRADUIRE[langue])
    assert set(compte) == set(INTENTS)
    assert min(compte.values()) >= 5


def test_environ_une_annonce_sur_trois_est_invalide_expres():
    part = sum(1 for a in FR if not a["pret_attendu"]) / len(FR)
    assert 0.2 <= part <= 0.45, f"part d'annonces a refuser : {part:.0%}"


def test_les_trois_pays_sont_representes():
    """Le projet couvre le Benin, le Nigeria et le Niger (cahier §3)."""
    indicatifs = Counter()
    for a in TOUT:
        tel = normaliser_brief(a["slots"]).get("phone")
        if isinstance(tel, str) and tel.startswith("+"):
            indicatifs[tel[:4]] += 1
    for indicatif in ("+229", "+234", "+227"):
        assert indicatifs[indicatif] >= 5, f"{indicatif} sous-represente : {indicatifs}"


def test_les_deux_devises_sont_representees():
    devises = Counter(normaliser_brief(a["slots"]).get("currency") for a in TOUT)
    assert devises["XOF"] >= 5 and devises["NGN"] >= 5, devises


# --------------------------------------------------------------------------- #
# Format impose par le guide d'annotation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("annonce", TOUT, ids=lambda a: f"{a['slots']['language']}{a['id']}")
def test_format_de_l_annonce(annonce):
    for cle in ("id", "transcript", "slots", "pret_attendu", "piege", "source", "annotateur"):
        assert cle in annonce, f"cle {cle} manquante"
    assert annonce["source"] in SOURCES
    assert annonce["annotateur"], "l'annotateur doit etre renseigne"
    assert isinstance(annonce["pret_attendu"], bool)


@pytest.mark.parametrize("annonce", TOUT, ids=lambda a: f"{a['slots']['language']}{a['id']}")
def test_une_annonce_refusee_explique_pourquoi(annonce):
    if not annonce["pret_attendu"]:
        assert annonce["piege"].strip(), "toute annonce refusee doit avoir un piege explique"


@pytest.mark.parametrize("fichier, annonces", [("fr", FR)] + list(A_TRADUIRE.items()))
def test_les_identifiants_sont_uniques(fichier, annonces):
    ids = [a["id"] for a in annonces]
    assert len(ids) == len(set(ids)), f"doublons dans {fichier}"


# --------------------------------------------------------------------------- #
# Regle absolue : aucun texte invente en Yoruba ou en Hausa
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("langue", ["yoruba", "hausa"])
def test_aucune_traduction_inventee(langue):
    """Personne dans l'equipe ne parle ces langues : le champ reste vide
    jusqu'a ce qu'un locuteur natif le remplisse (decisions.md D-008)."""
    for a in A_TRADUIRE[langue]:
        assert a["transcript"] is None, f"annonce {a['id']} : traduction non verifiee"
        assert a["source"] == "a_traduire"
        assert a["traducteur"] is None
        assert a["transcript_source_fr"].strip(), "le texte source doit exister"


# --------------------------------------------------------------------------- #
# Chaine complete : normaliser -> valider -> feu vert
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("annonce", TOUT, ids=lambda a: f"{a['slots']['language']}{a['id']}")
def test_le_moteur_donne_le_feu_vert_attendu(annonce):
    brief = normaliser_brief(annonce["slots"])
    pret = pret_pour_generation(brief) and not valider_brief(brief)
    assert pret == annonce["pret_attendu"], annonce["piege"]
