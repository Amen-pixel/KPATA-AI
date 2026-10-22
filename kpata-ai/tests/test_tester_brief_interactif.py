import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "tester_brief_interactif.py"
SPEC = importlib.util.spec_from_file_location("tester_brief_interactif", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
main = MODULE.main


def saisir_evenement(event_name):
    return iter([
        "francais", "4", "", "centre de formation", "", event_name,
        "", "", "", "samedi", "", "Cotonou", "0197000000", "", "",
    ])


def test_interactif_affiche_score_validation_et_annonce():
    entrees = saisir_evenement("Journée portes ouvertes")
    sortie = []
    main(input_fn=lambda _: next(entrees), output_fn=sortie.append)

    texte = "\n".join(sortie)
    assert "Poids appliqués pour « evenement »" in texte
    assert "event_name=3" in texte
    assert "Feu vert du moteur : oui" in texte
    assert "Aucune valeur présente invalide." in texte
    assert "Journée portes ouvertes à Cotonou le samedi." in texte


def test_interactif_refuse_evenement_sans_nom_et_n_invoque_pas_generation():
    entrees = saisir_evenement("")
    sortie = []
    main(input_fn=lambda _: next(entrees), output_fn=sortie.append)

    texte = "\n".join(sortie)
    assert "Champs manquants : event_name" in texte
    assert "Feu vert du moteur : non" in texte
    assert "Génération ignorée" in texte
    assert "Texte publicitaire généré" not in texte
