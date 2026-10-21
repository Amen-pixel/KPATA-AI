"""Controle de fidelite d'une traduction automatique (tache B, D-010).

Tous les cas sont fabriques a la main : aucun modele n'est telecharge, aucun
appel reseau. Ces tests tournent par defaut.
"""
import pytest

from kpata.controle_traduction import (chiffres_seuls, controler, nom_propre_present,
                                       nombres_critiques, nombres_du_texte, resumer)

# Annonce de reference : le cas du cahier des charges, transpose au Nigeria.
ANNONCE = {
    "id": 1,
    "transcript_source_fr": "J'ai une boutique de chaussures a Ibadan. "
                            "Moins 20% vendredi et samedi. Mon numero, +234 803 111 2233.",
    "slots": {
        "language": "yoruba", "intent": "promotion",
        "business_name": None, "business_type": "boutique de chaussures",
        "product": "chaussures", "promotion": "20%", "price": None, "currency": None,
        "start_date": "vendredi", "end_date": "samedi",
        "location": "Ibadan", "phone": "+234 803 111 2233",
        "tone": None, "requested_media": None,
    },
}

# Une traduction plausible qui conserve tout : chiffres et nom de ville.
BONNE_TRADUCTION = ("Mo ni ile itaja bata ni Ibadan. Eyi 20% ojo Eti ati ojo Abameta. "
                    "Nomba mi, +234 803 111 2233.")
BONNE_RETRO = ("J'ai une boutique de chaussures a Ibadan. 20% vendredi et samedi. "
               "Mon numero, +234 803 111 2233.")


# --------------------------------------------------------------------------- #
# Briques de base
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("brut, attendu", [
    ("+234 803 111 2233", "2348031112233"),
    ("0197000000", "0197000000"),
    ("5 000 F", "5000"),
    ("rien", ""),
])
def test_chiffres_seuls(brut, attendu):
    assert chiffres_seuls(brut) == attendu


@pytest.mark.parametrize("texte, attendu", [
    ("20% vendredi", ["20"]),
    ("5 000 F et 20%", ["5000", "20"]),          # '5 000' est un seul nombre
    ("le 15 octobre a 2500 F", ["15", "2500"]),
    ("aucun chiffre", []),
])
def test_nombres_du_texte(texte, attendu):
    assert nombres_du_texte(texte) == attendu


def test_nombres_critiques_de_l_annonce():
    trouves = dict((e, v) for e, v in nombres_critiques(ANNONCE))
    assert trouves["téléphone"] == "2348031112233"
    assert trouves["pourcentage"] == "20"


def test_nombres_critiques_inclut_le_jour_du_mois():
    annonce = {"slots": {"start_date": "15 octobre"}}
    assert ("jour (start_date)", "15") in nombres_critiques(annonce)


def test_nombres_critiques_ignore_un_jour_nomme():
    """'vendredi' n'a pas de chiffre : rien a verifier."""
    annonce = {"slots": {"start_date": "vendredi"}}
    assert nombres_critiques(annonce) == []


@pytest.mark.parametrize("nom, traduction, attendu", [
    ("Ibadan", "ni Ibadan loni", True),
    ("Ibadan", "ni Eko loni", False),
    ("Abomey-Calavi", "ni Abomey Calavi", True),      # decoupage different : accepte
    ("Saint-Michel, Cotonou", "ni Saint Michel, Cotonou", True),
    ("Lagos", "ni LAGOS", True),                      # casse ignoree
])
def test_nom_propre_present(nom, traduction, attendu):
    assert nom_propre_present(nom, traduction) is attendu


# --------------------------------------------------------------------------- #
# Les six cas demandes
# --------------------------------------------------------------------------- #
def test_cas_accepte():
    ok, raisons = controler(ANNONCE, BONNE_TRADUCTION, BONNE_RETRO)
    assert ok, raisons
    assert raisons == []


def test_prix_modifie_est_rejete():
    annonce = {**ANNONCE, "slots": {**ANNONCE["slots"], "price": "5000 F", "promotion": None}}
    traduction = "Bata ni Ibadan, 4000 F. Nomba mi, +234 803 111 2233."
    ok, raisons = controler(annonce, traduction, "Chaussures a Ibadan, 4000 F.")
    assert not ok
    assert any("prix 5000" in r for r in raisons), raisons


def test_numero_coupe_est_rejete():
    traduction = "Mo ni ile itaja bata ni Ibadan. Eyi 20%. Nomba mi, +234 803 111."
    ok, raisons = controler(ANNONCE, traduction, "Boutique a Ibadan, 20%, +234 803 111.")
    assert not ok
    assert any("téléphone" in r for r in raisons), raisons


def test_lieu_traduit_est_rejete():
    """Un nom de ville ne se traduit pas : s'il disparait, on rejette."""
    traduction = ("Mo ni ile itaja bata ni ilu nla. Eyi 20% ojo Eti. "
                  "Nomba mi, +234 803 111 2233.")
    ok, raisons = controler(ANNONCE, traduction, BONNE_RETRO)
    assert not ok
    assert any("Ibadan" in r for r in raisons), raisons


@pytest.mark.parametrize("vide", ["", None, "   "])
def test_traduction_vide_est_rejetee(vide):
    ok, raisons = controler(ANNONCE, vide, BONNE_RETRO)
    assert not ok
    assert raisons == ["traduction vide"]


def test_date_decalee_est_rejetee():
    annonce = {**ANNONCE, "slots": {**ANNONCE["slots"],
                                    "start_date": "15 octobre", "end_date": None}}
    traduction = ("Mo ni ile itaja bata ni Ibadan. Eyi 20% ni ojo 20 October. "
                  "Nomba mi, +234 803 111 2233.")
    retro = ("Boutique de chaussures a Ibadan. 20% le 20 octobre. "
             "Mon numero +234 803 111 2233.")
    ok, raisons = controler(annonce, traduction, retro)
    assert not ok
    assert any("jour" in r or "start_date" in r for r in raisons), raisons


# --------------------------------------------------------------------------- #
# Cas complementaires
# --------------------------------------------------------------------------- #
def test_traduction_identique_au_francais_est_rejetee():
    """Le modele a recopie l'entree : ce n'est pas une traduction."""
    source = ANNONCE["transcript_source_fr"]
    ok, raisons = controler(ANNONCE, source, source)
    assert not ok
    assert any("identique" in r for r in raisons), raisons


def test_retro_traduction_vide_est_rejetee():
    ok, raisons = controler(ANNONCE, BONNE_TRADUCTION, "")
    assert not ok
    assert any("retro" in r for r in raisons), raisons


def test_retro_qui_perd_le_numero_est_rejetee():
    retro = "J'ai une boutique de chaussures a Ibadan. 20% vendredi et samedi."
    ok, raisons = controler(ANNONCE, BONNE_TRADUCTION, retro)
    assert not ok
    assert any("phone" in r for r in raisons), raisons


def test_toutes_les_raisons_sont_listees():
    """Plusieurs problemes : on les signale tous, pas seulement le premier."""
    traduction = "Eyi ni oro kan."          # ni chiffres, ni lieu
    ok, raisons = controler(ANNONCE, traduction, "Ceci est un mot.")
    assert not ok
    assert len(raisons) >= 3, raisons


def test_annonce_sans_information_critique_est_acceptee():
    """Rien a verifier : on ne rejette pas pour autant."""
    annonce = {"transcript_source_fr": "Je propose mes services.",
               "slots": {"product": "services"}}
    ok, raisons = controler(annonce, "Mo n pese awon ise mi.", "Je propose mes services.")
    assert ok, raisons


def test_resumer_regroupe_les_raisons_de_meme_nature():
    rejets = [
        {"raisons": ["prix 5000 absent de la traduction"]},
        {"raisons": ["prix 300 absent de la traduction"]},
        {"raisons": ["lieu « Lagos » absent ou traduit"]},
    ]
    familles = dict(resumer(rejets))
    assert familles["prix N absent de la traduction"] == 2
    assert familles["lieu «…» absent ou traduit"] == 1
