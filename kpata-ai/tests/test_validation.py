from kpata.validation import valider_brief


def test_brief_valide():
    brief = {"language": "yoruba", "intent": "promotion", "phone": "0197000000", "promotion": "20%",
             "product": "chaussures", "location": "Calavi", "start_date": "15 octobre"}
    assert valider_brief(brief) == {}


def test_brief_invalide_signale_chaque_champ():
    brief = {"language": "swahili", "intent": "promotion", "phone": "12345", "promotion": "150%",
             "product": "x", "start_date": "30 février"}
    assert set(valider_brief(brief)) == {"language", "phone", "promotion", "product", "start_date"}


def test_champ_absent_nest_pas_invalide():
    assert valider_brief({"intent": "promotion"}) == {}


def test_nom_evenement_trop_court_est_invalide():
    assert valider_brief({"event_name": "x"}) == {
        "event_name": "nom de l'événement trop court"
    }
