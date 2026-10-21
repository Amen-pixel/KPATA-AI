# Fiche du jeu de données Kpata AI

Première version, Phase 0 → Phase 1. Recense chaque source de données avec son
origine, son volume, sa licence, sa méthode de contrôle et ses limites.

Document tenu par Zozerigué. Les lignes Common Voice et FLEURS sont à remplir
par Amen quand sa collecte sera faite (voir `note_pour_amen.md`).

> **Avertissement sur les licences.** Les deux modèles utilisés pour fabriquer
> les données (NLLB-200 et MMS-TTS) sont en **CC-BY-NC 4.0**, donc **usage non
> commercial**. C'est acceptable pour un projet d'école, mais cela **interdit
> toute exploitation commerciale** de Kpata AI entraîné sur ces données. Le
> cahier des charges demande explicitement de vérifier les licences avant toute
> réutilisation commerciale : c'est fait, et la réponse est non.

---

## Vue d'ensemble

| Source | Type | Yorùbá | Hausa | Français | Licence | Voix réelle ? |
| --- | --- | --- | --- | --- | --- | --- |
| Annonces écrites par l'équipe | texte | — | — | 50 | interne au projet | — |
| Annonces à traduire | texte | 50 | 50 | — | interne au projet | — |
| Traduction automatique NLLB | texte | *(tâche B)* | *(tâche B)* | — | CC-BY-NC 4.0 | — |
| Synthèse vocale MMS-TTS | audio | *(tâche C)* | *(tâche C)* | — | CC-BY-NC 4.0 | **non** |
| Common Voice | audio | *(à remplir)* | *(à remplir)* | — | CC0 | **oui** |
| FLEURS | audio | *(à remplir)* | *(à remplir)* | — | CC-BY 4.0 | **oui** |

Les volumes marqués *(tâche B)* et *(tâche C)* dépendent du taux d'acceptation
du contrôle de fidélité : ils sont donnés dans `bilan_phase0.md`, qui est
régénéré automatiquement.

---

## 1. Annonces écrites par l'équipe (français)

- **Origine** : écrites à la main par l'équipe, d'après le cahier des charges.
  Fichier : `data/briefs/briefs_fr.json`. Script : `scripts/generer_briefs.py`.
- **Volume** : 50 annonces. Les 7 intentions sont présentes au moins 5 fois
  chacune ; 12 annonces sur 50 sont incomplètes ou invalides exprès.
- **Licence** : production interne au projet, aucune restriction externe.
- **Contrôle** : chaque annonce passe par `normaliser → valider → feu vert`, et
  le résultat est comparé au `pret_attendu` annoté. 0 désaccord
  (`tests/test_jeu_de_donnees.py`).
- **Limites** : textes **écrits**, donc plus propres qu'une transcription
  réelle. Pas d'hésitation, pas de bruit, orthographe correcte. Les scores
  mesurés dessus sont optimistes. Aucun audio associé : `audio_path` est vide.

## 2. Annonces préparées pour la traduction (Yorùbá, Hausa)

- **Origine** : texte source en français, adapté au pays visé (Nigeria du
  Sud-Ouest pour le Yorùbá, Nigeria du Nord et Niger pour le Hausa). Fichiers :
  `data/briefs/a_traduire_yoruba.json`, `a_traduire_hausa.json`. Script :
  `scripts/preparer_traductions.py`.
- **Volume** : 50 par langue, avec les slots déjà annotés.
- **Licence** : production interne au projet.
- **Contrôle** : mêmes tests que les annonces françaises, plus une vérification
  qu'aucune traduction n'a été inventée (`transcript` doit rester `null`).
- **Limites** : ce ne sont **pas encore** des données en Yorùbá ni en Hausa.
  Seul le texte français existe ; le champ `transcript` est vide.

## 3. Traduction automatique — NLLB-200

- **Modèle** : `facebook/nllb-200-distilled-600M`
  (https://huggingface.co/facebook/nllb-200-distilled-600M)
- **Origine** : traduction du français vers `yor_Latn` et `hau_Latn`, puis
  retraduction vers le français pour contrôle. Script :
  `scripts/traduire_auto.py`.
- **Licence** : **CC-BY-NC 4.0 — non commercial.** Vérifiée sur la fiche
  officielle du modèle. Attribution requise.
- **Contrôle** (`src/kpata/controle_traduction.py`, D-010) : une annonce n'est
  acceptée que si **toutes** ces conditions sont vraies :
  1. chaque nombre critique (téléphone, prix, pourcentage, jour du mois)
     apparaît à l'identique dans la traduction, chiffres comparés sans espaces ;
  2. le lieu et le nom du commerce apparaissent tels quels ;
  3. la retraduction en français, passée dans `normaliser_brief`, redonne les
     mêmes valeurs pour `phone`, `price`, `promotion`, `start_date`, `end_date` ;
  4. la traduction n'est ni vide ni identique au texte français.

  Une annonce qui échoue est **rejetée**, jamais corrigée à la main. Les rejets
  et leurs raisons sont conservés dans `data/briefs/rejets_traduction.json`.
- **Limites** :
  - le contrôle vérifie que les **informations critiques** survivent, **pas**
    que la phrase est bien tournée. Une traduction peut passer tous les
    contrôles et rester maladroite, voire incompréhensible pour un locuteur ;
  - **personne dans l'équipe ne peut relire ces textes.** C'est la limite qui
    englobe toutes les autres ;
  - le Yorùbá est une langue à tons, et la traduction automatique les rend mal :
    deux mots distincts à l'oral peuvent se confondre à l'écrit ;
  - le taux d'acceptation est un **résultat en soi**, donné dans
    `bilan_phase0.md`. Il n'a pas été amélioré en assouplissant les règles.
- **Marquage** : `source = "traduit_auto"`. Distinct de
  `traduit_non_verifie`, qui désigne une traduction sans aucun contrôle.

## 4. Synthèse vocale — MMS-TTS

- **Modèles** : `facebook/mms-tts-yor` et `facebook/mms-tts-hau`
  (https://huggingface.co/facebook/mms-tts-yor)
- **Origine** : lecture automatique des traductions acceptées. Script :
  `scripts/synthese_vocale.py`. Audio WAV mono 16 kHz, dans
  `data/audio/synthese/`, **hors de Git**. Manifeste :
  `data/briefs/manifeste_synthese.csv`.
- **Licence** : **CC-BY-NC 4.0 — non commercial.** Vérifiée sur la fiche
  officielle. Attribution requise.
- **Contrôle** : la fréquence et le nombre de canaux sont vérifiés par les
  tests ; le nommage suit la convention de `data/README.md` avec `SYNTH` comme
  identifiant de locuteur. La graine aléatoire est fixée à 42, car le
  prédicteur de durée de VITS est stochastique : sans graine, le jeu de données
  ne serait pas reproductible.
- **Limites, les plus importantes de ce document** :
  - **une seule voix par langue.** Les séparations par locuteur exigées au §6
    du cahier des charges sont **impossibles** sur ces données ;
  - **ces voix sont beaucoup plus propres qu'un vrai commerçant** : pas de bruit
    de marché, pas d'hésitation, pas d'accent régional, débit régulier,
    enregistrement parfait. Tout score de transcription obtenu dessus est
    **trop optimiste** et ne prédit pas la performance en situation réelle ;
  - la prononciation dépend de la qualité de la traduction en amont : une
    traduction maladroite donne un audio maladroit ;
  - le modèle lit ce qu'on lui donne, y compris une faute : il n'y a aucun
    contrôle de prononciation possible sans locuteur.
- **Marquage** : `source = "synthese_vocale"`.

## 5. Common Voice *(collecte d'Amen — à remplir)*

- **Modèle / corpus** : Mozilla Common Voice, sous-ensembles Yorùbá et Hausa
  (https://commonvoice.mozilla.org/datasets)
- **Origine** : enregistrements de locuteurs volontaires, avec transcription.
- **Volume** : *à remplir par Amen.*
- **Licence** : **CC0** (domaine public) pour les corpus Common Voice. À
  confirmer sur la page de la version précise téléchargée, car elle varie selon
  les millésimes.
- **Contrôle** : *à définir avec Amen.* Les clips Common Voice sont notés par
  les contributeurs (validés / rejetés) : il faut ne garder que les validés.
- **Limites** : phrases lues, pas des annonces commerciales spontanées. Le
  vocabulaire ne correspond pas à notre domaine, mais **ce sont de vraies
  voix**, ce qui est irremplaçable pour évaluer la transcription.

## 6. FLEURS *(proposé à Amen — à remplir)*

- **Corpus** : `google/fleurs`, langues `yo_ng` et `ha_ng`
  (https://huggingface.co/datasets/google/fleurs)
- **Origine** : phrases lues à voix haute, avec transcription, déjà découpées en
  entraînement / validation / test.
- **Volume** : *à remplir par Amen.*
- **Licence** : **CC-BY 4.0.** Vérifiée sur la fiche du corpus. Attribution
  requise, usage commercial autorisé — plus permissive que nos modèles.
- **Contrôle** : découpage déjà fourni par les auteurs, donc rien à refaire.
- **Limites** : phrases issues de Wikipédia, hors de notre domaine commercial.
  Métadonnées de locuteur moins détaillées que Common Voice, ce qui limite les
  splits par locuteur. Comme Common Voice, **ce sont de vraies voix**.

---

## Récapitulatif des licences

| Ressource | Licence | Commercial ? | Attribution ? |
| --- | --- | --- | --- |
| `facebook/nllb-200-distilled-600M` | CC-BY-NC 4.0 | **non** | oui |
| `facebook/mms-tts-yor` | CC-BY-NC 4.0 | **non** | oui |
| `facebook/mms-tts-hau` | CC-BY-NC 4.0 | **non** | oui |
| Mozilla Common Voice | CC0 | oui | non requise |
| `google/fleurs` | CC-BY 4.0 | oui | oui |
| Annonces écrites par l'équipe | interne | oui | — |

**Conséquence à retenir** : tant que le jeu de données contient des traductions
NLLB ou des audios MMS-TTS, **Kpata AI ne peut pas être exploité
commercialement**. Pour lever cette contrainte il faudrait refaire les données
avec des traductions humaines et de vrais enregistrements — c'est-à-dire
exactement ce que l'absence de locuteur nous empêche de faire aujourd'hui.

## Ce qui manque encore

1. **Des voix réelles en Yorùbá et en Hausa** : Common Voice et FLEURS, à
   collecter par Amen. Sans elles, aucune évaluation honnête de la
   transcription n'est possible.
2. **Une relecture humaine**, même sur un échantillon : le protocole est prêt
   (`docs/verification/`), il manque le relecteur.
3. **Le tableau de référence du jeu de données** (`data/tableau_reference/`),
   qui est la tâche d'Amen pour la Phase 1.
