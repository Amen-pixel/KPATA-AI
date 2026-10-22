from kpata import brief as brief_compat
from kpata.completude import completude, champs_manquants, pret_pour_generation
from kpata.schema import CHAMPS, POIDS_PAR_INTENTION, nouveau_brief
import pytest


def promo_complete():
    return nouveau_brief(language="francais", intent="promotion", business_type="boutique de chaussures",
                         product="chaussures", promotion="-20 %", location="Abomey-Calavi",
                         phone="+2290197000000", start_date="vendredi", end_date="samedi")


def test_promo_complete():
    b = promo_complete()
    assert pret_pour_generation(b) and champs_manquants(b) == []


def test_jamais_sans_telephone():
    b = {**promo_complete(), "phone": None}
    assert not pret_pour_generation(b)
    assert champs_manquants(b) == ["phone"]


def test_un_champ_qui_ne_contient_que_des_espaces_est_manquant():
    b = {**promo_complete(), "phone": "   "}
    assert not pret_pour_generation(b)
    assert champs_manquants(b) == ["phone"]


def test_restock_sans_promo_est_accepte():
    b = nouveau_brief(language="francais", intent="restock", product="wax",
                      location="Dantokpa", phone="+2290196000000")
    assert pret_pour_generation(b)


def test_promotion_ou_prix_suffit():
    b = {**promo_complete(), "promotion": None, "price": 2500}
    assert pret_pour_generation(b)


def test_ouverture_accepte_un_nom_ou_un_type_de_commerce():
    b = nouveau_brief(language="francais", intent="ouverture", business_name="Chez Awa",
                      location="Cotonou", phone="0197000000")
    assert champs_manquants(b) == []
    assert pret_pour_generation(b)


def test_offre_limitee_accepte_une_seule_borne_de_date():
    b = nouveau_brief(language="francais", intent="offre_limitee", product="wax",
                      promotion="20%", start_date="vendredi", location="Cotonou",
                      phone="0197000000")
    assert champs_manquants(b) == []
    assert pret_pour_generation(b)


def test_evenement_exige_un_nom_et_une_date():
    b = nouveau_brief(language="francais", intent="evenement",
                      start_date="samedi", location="Cotonou",
                      phone="0197000000")
    assert champs_manquants(b) == ["event_name"]
    assert not pret_pour_generation(b)
    b["event_name"] = "Journée portes ouvertes"
    assert champs_manquants(b) == []
    assert pret_pour_generation(b)


def test_intent_inconnu_bloque():
    assert not pret_pour_generation({**promo_complete(), "intent": "nimportequoi"})


def test_completude_entre_0_et_1():
    assert 0 <= completude(promo_complete()) <= 1


def test_completude_applique_les_poids_et_inclut_la_devise_optionnelle():
    b = promo_complete()
    assert completude(b) == pytest.approx(16 / 20)
    b["currency"] = "XOF"
    assert completude(b) == pytest.approx(17 / 20)


def test_les_poids_sont_specifiques_a_l_intention():
    evenement = nouveau_brief(
        language="francais", intent="evenement", event_name="Foire",
        start_date="samedi", location="Cotonou", phone="0197000000",
    )
    evenement_sans_nom = {**evenement, "event_name": None}
    assert completude(evenement) > completude(evenement_sans_nom)

    restock = nouveau_brief(
        language="francais", intent="restock", product="wax",
        location="Cotonou", phone="0197000000",
    )
    restock_avec_nom_evenement = {**restock, "event_name": "Foire"}
    assert completude(restock) == completude(restock_avec_nom_evenement)
    assert POIDS_PAR_INTENTION["evenement"]["event_name"] == 3
    assert "event_name" not in POIDS_PAR_INTENTION["restock"]


@pytest.mark.parametrize("modifications", [
    {"language": None},
    {"intent": "inconnu"},
    {"language": "   "},
])
def test_completude_n_est_pas_calculee_sans_contexte(modifications):
    assert completude({**promo_complete(), **modifications}) == 0.0


def test_champ_inconnu_refuse():
    with pytest.raises(ValueError):
        nouveau_brief(telephone="0197000000")


def test_ancien_module_brief_reste_compatible():
    assert brief_compat.CHAMPS is CHAMPS
    assert brief_compat.completude is completude
    assert brief_compat.nouveau_brief is nouveau_brief
