"""Le champ currency (tache A2) : schema, validation, coherence."""
import pytest

from kpata.schema import CHAMPS, POIDS, nouveau_brief
from kpata.normalisation import DEVISES
from kpata.validation import valider_brief


def test_currency_est_dans_le_schema():
    assert "currency" in CHAMPS


def test_currency_a_un_poids():
    assert POIDS["currency"] == 1


def test_nouveau_brief_accepte_currency():
    assert nouveau_brief(currency="XOF")["currency"] == "XOF"


@pytest.mark.parametrize("devise", DEVISES)
def test_devise_connue_est_valide(devise):
    assert valider_brief({"currency": devise}) == {}


@pytest.mark.parametrize("devise", ["EUR", "USD", "xof", "franc"])
def test_devise_inconnue_est_refusee(devise):
    assert "currency" in valider_brief({"currency": devise})


def test_tous_les_champs_ponderes_existent():
    """POIDS ne doit pas parler d'un champ qui n'est pas dans le schema."""
    assert set(POIDS) <= set(CHAMPS)


def test_prix_nombre_seul_est_valide_dans_le_champ_price():
    """Dans le champ price, un nombre seul est un prix (voir D-002)."""
    assert valider_brief({"price": "3000"}) == {}
    assert valider_brief({"price": 3000}) == {}
