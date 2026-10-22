import pytest

from kpata.generation_texte import generer_texte_publicitaire
from kpata.schema import nouveau_brief


def brief(intent, **champs):
    return nouveau_brief(language="yoruba", intent=intent, location="Cotonou",
                         phone="0197000000", **champs)


@pytest.mark.parametrize(("annonce", "attendu"), [
    (brief("promotion", product="chaussures", promotion="20%", start_date="vendredi"),
     "OFFRE SPÉCIALE\n-20 % sur chaussures\nÀ partir du vendredi."),
    (brief("offre_limitee", product="wax", price="5000 F", start_date="vendredi",
           end_date="samedi"),
     "OFFRE LIMITÉE\nwax au prix de 5 000 F CFA\nDu vendredi au samedi."),
    (brief("lancement", product="nouveau modèle"),
     "NOUVEAUTÉ\nnouveau modèle fait son entrée dans notre offre."),
    (brief("ouverture", business_name="Chez Awa", start_date="samedi"),
     "Chez Awa\nOUVERTURE\nOuverture de Chez Awa.\nÀ partir du samedi."),
    (brief("evenement", event_name="Foire artisanale", start_date="dimanche"),
     "RENDEZ-VOUS\nFoire artisanale à Cotonou le dimanche."),
    (brief("restock", product="wax"),
     "DE RETOUR\nwax est de nouveau disponible."),
    (brief("annonce_service", product="coiffure"),
     "NOS SERVICES\nDécouvrez notre offre de coiffure."),
])
def test_generation_par_intention(annonce, attendu):
    texte = generer_texte_publicitaire(annonce)
    assert attendu in texte
    assert "Lieu : Cotonou" in texte
    assert "Contact : +2290197000000" in texte


def test_le_texte_est_en_francais_meme_si_le_brief_est_dans_une_autre_langue():
    texte = generer_texte_publicitaire(
        brief("restock", product="wax", tone="chaleureux")
    )
    assert "DE RETOUR" in texte
    assert "Au plaisir de vous accueillir !" in texte


def test_un_prix_sans_devise_ne_recoit_pas_de_devise_inventee():
    texte = generer_texte_publicitaire(
        brief("restock", product="wax", price=3000)
    )
    assert "Prix : 3 000." in texte
    assert "F CFA" not in texte
    assert "₦" not in texte


def test_brief_incomplet_est_refuse():
    annonce = brief("restock", product="wax")
    annonce["phone"] = None
    with pytest.raises(ValueError, match="brief incomplet.*phone"):
        generer_texte_publicitaire(annonce)


def test_evenement_sans_nom_est_refuse():
    annonce = brief("evenement", start_date="dimanche")
    with pytest.raises(ValueError, match="event_name"):
        generer_texte_publicitaire(annonce)


def test_brief_invalide_est_refuse():
    annonce = brief("promotion", product="chaussures", promotion="150%")
    with pytest.raises(ValueError, match="promotion"):
        generer_texte_publicitaire(annonce)


@pytest.mark.parametrize("prix", [True, 2500.0])
def test_prix_qui_ne_sont_pas_des_entiers_sont_refuses(prix):
    annonce = brief("restock", product="wax", price=prix)
    with pytest.raises(ValueError, match="price"):
        generer_texte_publicitaire(annonce)


def test_champ_etranger_au_schema_est_refuse():
    with pytest.raises(ValueError, match="champ inconnu"):
        generer_texte_publicitaire({"intent": "restock", "surprise": "oui"})


def test_aucune_valeur_absente_n_est_affichee_comme_texte():
    texte = generer_texte_publicitaire(brief("ouverture", business_name="Chez Awa"))
    assert "None" not in texte
    assert "business_type" not in texte
