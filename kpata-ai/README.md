# Kpata AI

Agent vocal de création publicitaire en Yorùbá et Hausa — AMA · PIIA Cohorte 2 (Machine Learning).
L'utilisateur parle dans sa langue, Kpata comprend la demande, construit un brief structuré, puis
produit une campagne en français. Release finale : 27 février 2027.

## Équipe

| Membre | Rôle |
| --- | --- |
| QUENUM Amen | Data engineer |
| TRAORE Zozerigué | Data analyst et Data scientist |
| MEMEDE Eudes Isaï Damasse | AI engineer |

## Installation (une seule fois)

```bash
git clone <url-du-depot>
cd kpata-ai
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -e . pytest
pytest                           # tout doit être vert
```

## Où ranger quoi

| Dossier | Contenu | Propriétaire |
| --- | --- | --- |
| `src/kpata/normalisation.py`, `validation.py` | normalisation et validation (téléphone, prix, devise, dates, périodes, pourcentages) | Amen |
| `src/kpata/brief.py` | schéma du brief, moteur de complétude | constantes tenues par Zozerigué, logique à reprendre par Eudes |
| `tests/` | tests automatiques (`pytest`) | celui qui écrit le code |
| `data/briefs/` | annonces d'exemple annotées (fichiers JSON, légers) | les trois |
| `data/audio/` | enregistrements : **jamais sur GitHub**, uniquement dans le dossier partagé (Drive) | Amen |
| `data/tableau_reference/` | tableau de référence du jeu de données (Phase 1) | Amen |
| `docs/` | schéma de l'annonce, guide d'annotation, décisions, bilans | Zozerigué |
| `scripts/` | petits scripts utilitaires | chacun |
| `notebooks/` | essais et analyses (Jupyter) | chacun |

## Les documents à lire avant de coder

| Document | À quoi il sert |
| --- | --- |
| `docs/schema_annonce.md` | **La référence.** Les champs d'un brief, leur forme normalisée, leur poids, la règle du feu vert. |
| `docs/guide_annotation.md` | Comment annoter une annonce, pour que les trois annotent pareil. |
| `docs/decisions.md` | Toutes les décisions de conception, avec leur raison et leur statut. |
| `docs/fiche_donnees.md` | Chaque source de données : volume, **licence**, contrôle, limites. |
| `docs/bilan_phase0.md` | L'état du jeu de données et du moteur. Généré, ne pas modifier à la main. |

## Scripts

```bash
python scripts/generer_briefs.py        # réécrit data/briefs/briefs_fr.json (50 annonces)
python scripts/preparer_traductions.py  # réécrit les 2 fichiers à faire traduire (50 + 50)
python scripts/bilan_phase0.py          # réécrit docs/bilan_phase0.md
```

Après avoir modifié une annonce, relancer le script correspondant **et**
`scripts/bilan_phase0.py`, puis `pytest`.

### Scripts qui ont besoin d'un modèle (Phase 1)

Ceux-ci demandent les bibliothèques lourdes, installées séparément :

```bash
pip install -r requirements-phase1.txt

python scripts/traduire_auto.py            # traduit vers le Yorùbá et le Hausa (NLLB-200)
python scripts/synthese_vocale.py          # génère les audios (MMS-TTS)
python scripts/echantillon_verification.py # tire 20 annonces à faire relire
python scripts/resultats_verification.py   # lit les fichiers remplis par le relecteur
```

Le paquet `kpata` et `pytest` fonctionnent **sans** ces bibliothèques. Les tests
ne téléchargent jamais de modèle.

> **Attention aux licences.** NLLB-200 et MMS-TTS sont en **CC-BY-NC 4.0**, donc
> usage **non commercial**. Acceptable pour un projet d'école, mais cela
> interdit toute exploitation commerciale de Kpata AI entraîné sur ces données.
> Détail dans `docs/fiche_donnees.md`.

## Règles de travail

1. **Une branche par personne et par tâche** : `amen/normalisation`, `zozerigue/guide-annotation`,
   `eudes/moteur-completude`. On ne travaille pas directement sur `main`.
2. **Avant de fusionner dans `main`** : `pytest` doit passer, et une autre personne relit (Pull Request).
3. **Messages de commit clairs** : « Ajoute la normalisation des dates », pas « maj ».
4. **Aucun secret** (clés d'API, mots de passe) dans le dépôt. Ils vont dans un fichier `.env`, déjà ignoré par Git.
5. **Aucun fichier audio dans Git.** Chemins et noms de fichiers : voir `data/README.md`.
6. Si tu changes le format du brief, préviens les deux autres : le code des trois en dépend.
