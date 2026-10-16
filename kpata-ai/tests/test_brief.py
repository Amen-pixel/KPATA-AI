from kpata.brief import nouveau_brief, completude, champs_manquants, pret_pour_generation
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


def test_restock_sans_promo_est_accepte():
    b = nouveau_brief(language="francais", intent="restock", product="wax",
                      location="Dantokpa", phone="+2290196000000")
    assert pret_pour_generation(b)


def test_promotion_ou_prix_suffit():
    b = {**promo_complete(), "promotion": None, "price": 2500}
    assert pret_pour_generation(b)


def test_intent_inconnu_bloque():
    assert not pret_pour_generation({**promo_complete(), "intent": "nimportequoi"})


def test_completude_entre_0_et_1():
    assert 0 <= completude(promo_complete()) <= 1


def test_champ_inconnu_refuse():
    with pytest.raises(ValueError):
        nouveau_brief(telephone="0197000000")
