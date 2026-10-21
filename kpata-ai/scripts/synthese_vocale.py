"""Génère les audios de synthèse pour les annonces traduites (tâche C).

Modèles : MMS-TTS de Meta, un par langue — `facebook/mms-tts-yor` et
`facebook/mms-tts-hau`. Licence CC-BY-NC 4.0 : usage NON commercial.

Ce que dit leur fiche de modèle, et qui compte ici :
- architecture VITS, sortie **nativement en 16 kHz mono** : aucun
  rééchantillonnage nécessaire ;
- le prédicteur de durée est **stochastique** : sans graine fixe, deux appels
  sur le même texte donnent deux audios différents. On fixe donc la graine pour
  que le jeu de données soit reproductible ;
- `is_uroman` est `False` pour le Yorùbá et le Hausa : le texte est passé tel
  quel, aucune romanisation préalable n'est requise.

Rappel (D-010) : ces voix sont plus propres qu'un vrai commerçant. Tout score
mesuré sur ces audios est **optimiste** et ne prédit pas la performance réelle.

Usage, depuis la racine du dépôt :
    pip install -r requirements-phase1.txt
    python scripts/synthese_vocale.py
    python scripts/synthese_vocale.py --langue hausa --limite 5
"""
import argparse
import csv
import json
import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
sys.path.insert(0, str(RACINE / "src"))

MODELES = {"yoruba": "facebook/mms-tts-yor", "hausa": "facebook/mms-tts-hau"}
LICENCE = "CC-BY-NC-4.0"

DOSSIER_BRIEFS = RACINE / "data" / "briefs"
DOSSIER_AUDIO = RACINE / "data" / "audio" / "synthese"
NOM_MANIFESTE = "manifeste_synthese.csv"

# Graine fixe : le prédicteur de durée de VITS est stochastique, sans graine le
# jeu de données ne serait pas reproductible.
GRAINE = 42

COLONNES = ["audio_path", "language", "transcript", "id_annonce", "source",
            "duree_s", "modele"]


class Synthetiseur:
    """Un modèle MMS-TTS pour une langue. Chargé une seule fois."""

    def __init__(self, langue):
        from transformers import AutoTokenizer, VitsModel
        self.nom = MODELES[langue]
        self.langue = langue
        print(f"Chargement de {self.nom}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.nom)
        self.modele = VitsModel.from_pretrained(self.nom)
        self.modele.eval()
        self.frequence = self.modele.config.sampling_rate
        print(f"  prêt, sortie à {self.frequence} Hz")

    def synthetiser(self, texte):
        """Renvoie (signal numpy float32, fréquence)."""
        import torch
        torch.manual_seed(GRAINE)          # reproductible malgré le stochastique
        entrees = self.tokenizer(texte, return_tensors="pt")
        with torch.no_grad():
            sortie = self.modele(**entrees).waveform
        return sortie.squeeze().cpu().numpy(), self.frequence


def nom_fichier(langue, numero):
    """Convention de data/README.md : <langue>_<locuteur>_<numéro>.wav
    Le locuteur est `SYNTH` : ce n'est pas une voix humaine, et le nom le dit."""
    return f"{langue}_SYNTH_{numero:03d}.wav"


def ecrire_wav(chemin, signal, frequence):
    """Écrit un WAV mono 16 bits. soundfile si disponible, sinon le module
    `wave` de la bibliothèque standard — pour ne pas dépendre d'une seule
    bibliothèque."""
    try:
        import soundfile as sf
        sf.write(str(chemin), signal, frequence, subtype="PCM_16")
    except ImportError:
        import wave
        import numpy as np
        # float32 dans [-1, 1] -> entiers 16 bits
        borne = np.clip(signal, -1.0, 1.0)
        entiers = (borne * 32767).astype("<i2")
        with wave.open(str(chemin), "wb") as f:
            f.setnchannels(1)              # mono
            f.setsampwidth(2)              # 16 bits
            f.setframerate(frequence)
            f.writeframes(entiers.tobytes())


def traiter_langue(langue, limite=None):
    """Synthétise toutes les annonces acceptées d'une langue."""
    source = DOSSIER_BRIEFS / f"briefs_{langue}_auto.json"
    if not source.exists():
        print(f"  {source.name} absent : lance d'abord scripts/traduire_auto.py")
        return []

    annonces = json.loads(source.read_text(encoding="utf-8"))
    if limite:
        annonces = annonces[:limite]
    if not annonces:
        print(f"  aucune annonce acceptée en {langue}")
        return []

    DOSSIER_AUDIO.mkdir(parents=True, exist_ok=True)
    synth = Synthetiseur(langue)
    lignes = []

    for i, annonce in enumerate(annonces, 1):
        texte = annonce["transcript"]
        signal, frequence = synth.synthetiser(texte)
        fichier = nom_fichier(langue, annonce["id"])
        ecrire_wav(DOSSIER_AUDIO / fichier, signal, frequence)
        duree = len(signal) / frequence

        lignes.append({
            "audio_path": f"synthese/{fichier}",
            "language": langue,
            "transcript": texte,
            "id_annonce": annonce["id"],
            "source": "synthese_vocale",
            "duree_s": f"{duree:.2f}",
            "modele": f"{synth.nom} ({LICENCE})",
        })
        print(f"  [{i:>2}/{len(annonces)}] {fichier}  {duree:5.2f} s")

    return lignes


def _joli_chemin(chemin):
    """Chemin relatif au dépôt quand c'est possible, absolu sinon (tests)."""
    try:
        return chemin.relative_to(RACINE)
    except ValueError:
        return chemin


def ecrire_manifeste(lignes):
    """Le manifeste est petit : il peut aller dans Git. On en met une copie
    dans data/briefs/, qui est versionné, en plus de data/audio/ qui ne l'est
    pas."""
    for dossier in (DOSSIER_AUDIO, DOSSIER_BRIEFS):
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = dossier / NOM_MANIFESTE
        with open(chemin, "w", encoding="utf-8", newline="") as f:
            redacteur = csv.DictWriter(f, fieldnames=COLONNES)
            redacteur.writeheader()
            redacteur.writerows(lignes)
        print(f"manifeste -> {_joli_chemin(chemin)}")


def main():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--langue", choices=["yoruba", "hausa"])
    parseur.add_argument("--limite", type=int)
    args = parseur.parse_args()

    langues = [args.langue] if args.langue else ["yoruba", "hausa"]
    toutes = []
    for langue in langues:
        print(f"\n=== {langue} ===")
        toutes += traiter_langue(langue, args.limite)

    if not toutes:
        print("\nRien à synthétiser.")
        return

    ecrire_manifeste(toutes)

    print("\n=== Résumé ===")
    for langue in langues:
        lignes = [l for l in toutes if l["language"] == langue]
        if lignes:
            total = sum(float(l["duree_s"]) for l in lignes)
            print(f"  {langue:8} {len(lignes):>3} fichiers, {total / 60:.1f} min "
                  f"(moyenne {total / len(lignes):.1f} s)")

    poids = sum(f.stat().st_size for f in DOSSIER_AUDIO.glob("*.wav"))
    print(f"\n  {DOSSIER_AUDIO.relative_to(RACINE)} : {poids / 1e6:.1f} Mo")
    print("  Ces fichiers ne sont PAS dans Git : à déposer sur le Drive de l'équipe.")


if __name__ == "__main__":
    main()
