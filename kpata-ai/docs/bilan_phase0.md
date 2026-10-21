# Bilan de la Phase 0 — Kpata AI

Généré automatiquement par `scripts/bilan_phase0.py` le 21/10/2026.
Ne pas modifier à la main : relancer le script.

**150 annonces analysées**, seuil du feu vert en vigueur : **0.5**.

---

## 1. Nombre d'annonces

### Par langue

| Langue | Annonces |
| --- | --- |
| francais | 50 |
| hausa | 50 |
| yoruba | 50 |


### Par intention et par langue

| Intention | francais | hausa | yoruba | Total |
| --- | --- | --- | --- | --- |
| promotion | 15 | 13 | 13 | 41 |
| lancement | 6 | 5 | 5 | 16 |
| ouverture | 6 | 6 | 6 | 18 |
| evenement | 6 | 6 | 6 | 18 |
| restock | 6 | 7 | 7 | 20 |
| annonce_service | 6 | 8 | 8 | 22 |
| offre_limitee | 5 | 5 | 5 | 15 |


### Par origine du texte

| Source | Annonces |
| --- | --- |
| a_traduire | 100 |
| ecrit_equipe | 50 |


> `a_traduire` : texte source en français, en attente d'un locuteur natif. Ces annonces ne sont pas utilisables pour mesurer une performance par langue.

---

## 2. Feu vert : calculé contre attendu

| Mesure | Nombre | Part |
| --- | --- | --- |
| Prêtes pour la génération | 108 | 72% |
| Non prêtes | 42 | 28% |
| **Accords** avec `pret_attendu` | 150 | 100% |
| **Désaccords** | 0 | 0% |


Aucun désaccord : le moteur donne exactement le feu vert attendu sur l'ensemble des annonces.

---

## 3. Champs qui manquent le plus souvent

| Champ | Annonces concernées | Poids dans C |
| --- | --- | --- |
| location | 13 | 3 |
| product | 10 | 3 |
| promotion ou price | 9 | — |
| start_date ou end_date | 4 | — |
| start_date | 3 | 2 |
| phone | 2 | 3 |


### Taux de remplissage de chaque champ

| Champ | Rempli | Part |
| --- | --- | --- |
| language | 150 | 100% |
| intent | 150 | 100% |
| business_type | 150 | 100% |
| phone | 148 | 99% |
| location | 137 | 91% |
| product | 116 | 77% |
| start_date | 51 | 34% |
| price | 48 | 32% |
| promotion | 43 | 29% |
| end_date | 6 | 4% |
| business_name | 0 | 0% |
| currency | 0 | 0% |
| tone | 0 | 0% |
| requested_media | 0 | 0% |


> Champs critiques jamais renseignés : business_name.

---

## 4. Valeurs que la normalisation n'a pas traitées

**11 valeurs** sur 150 annonces. Une valeur non traitée n'est pas forcément un bug : la plupart sont des cas invalides volontaires, que la validation doit refuser.

| Champ | Valeurs non traitées |
| --- | --- |
| phone | 5 |
| promotion | 3 |
| start_date | 3 |


### Exemples

| Fichier | id | Champ | Valeur brute |
| --- | --- | --- | --- |
| a_traduire_hausa.json | 8 | promotion | `200%` |
| a_traduire_hausa.json | 9 | phone | `55` |
| a_traduire_hausa.json | 33 | start_date | `32 mars` |
| a_traduire_hausa.json | 46 | phone | `777` |
| a_traduire_yoruba.json | 8 | promotion | `150%` |
| a_traduire_yoruba.json | 9 | phone | `12345` |
| a_traduire_yoruba.json | 33 | start_date | `30 février` |
| a_traduire_yoruba.json | 46 | phone | `999` |
| briefs_fr.json | 14 | promotion | `150%` |
| briefs_fr.json | 15 | phone | `12345` |
| briefs_fr.json | 26 | start_date | `30 février` |


---

## 5. Répartition des scores de complétude C

Sur l'ensemble : **minimum 0.25**, **moyenne 0.64**, **maximum 0.84**.

### Par intention

| Intention | Annonces | C min | C moyen | C max |
| --- | --- | --- | --- | --- |
| promotion | 41 | 0.37 | 0.67 | 0.84 |
| lancement | 16 | 0.25 | 0.55 | 0.62 |
| ouverture | 18 | 0.33 | 0.67 | 0.75 |
| evenement | 18 | 0.54 | 0.67 | 0.69 |
| restock | 20 | 0.44 | 0.58 | 0.62 |
| annonce_service | 22 | 0.25 | 0.58 | 0.62 |
| offre_limitee | 15 | 0.56 | 0.78 | 0.83 |


### Par langue

| Langue | Annonces | C min | C moyen | C max |
| --- | --- | --- | --- | --- |
| francais | 50 | 0.25 | 0.66 | 0.84 |
| hausa | 50 | 0.25 | 0.64 | 0.84 |
| yoruba | 50 | 0.25 | 0.64 | 0.84 |


### Distribution

| Tranche de C | Annonces |
| --- | --- |
| 0.2 à 0.3 | 5 |
| 0.3 à 0.4 | 5 |
| 0.4 à 0.5 | 6 |
| 0.5 à 0.6 | 14 |
| 0.6 à 0.7 | 85 |
| 0.7 à 0.8 | 18 |
| 0.8 à 0.9 | 17 |


Annonces sous le seuil (0.5) : **16** sur 150.

---

## 6. Annotation

| Annotateur | Annonces | Accords moteur/attendu |
| --- | --- | --- |
| AQ | 20 | 20 |
| TZ | 130 | 130 |


> La double annotation (1 annonce sur 5) n'a pas encore été faite : les annonces ont un seul annotateur. Le taux d'accord entre annotateurs sera mesuré ici dès que la seconde passe sera faite.

---

## 7. Générateur de texte (à compléter par Eudes)

_Section réservée._ Le générateur de texte à base de templates (cahier §5) n'est pas encore disponible. Quand il le sera, cette section devra présenter :

- le nombre de campagnes générées sans intervention humaine ;
- les champs critiques correctement reportés sur l'affiche (`CriticalFieldAccuracy`, cahier §7.2) ;
- les cas où le texte généré a inventé une information absente du brief ;
- le résultat du QA Agent (cahier §12) sur chaque campagne.

---

## 8. Ce qui reste à faire avant la Phase 1

### Bloquant

1. **Faire traduire les 100 annonces** en Yorùbá et en Hausa par des locuteurs natifs. Sans elles, le projet n'a aucune donnée dans ses langues cibles, et l'évaluation séparée par langue exigée au §9 du cahier est impossible. Il faut identifier un locuteur Yorùbá et un locuteur Hausa.
2. **Valider les décisions en attente** de `docs/decisions.md` : elles sont toutes au statut « proposé ». Les plus structurantes sont le barème des poids et le seuil (D-005), car le code des trois membres en dépend.

### À faire

3. **Double annotation** d'une annonce sur cinq, puis mesure du taux d'accord par champ (section 6).
4. **Enregistrer les notes vocales** : `audio_path` est vide partout, les annonces sont écrites à la main. La Phase 1 demande de vrais enregistrements, avec un identifiant de locuteur anonymisé pour permettre les splits par locuteur.
5. **Tableau de référence du jeu de données** (`data/tableau_reference/`), attendu en Phase 1.
6. **Générateur de texte à base de templates** (cahier §5), qui complétera la section 7 de ce bilan.

### Points de vigilance

7. Les annonces sont **écrites par l'équipe**, donc plus propres que de vraies transcriptions. Les scores de cette page sont optimistes : l'ASR de la Phase 1 produira des textes bruités, avec des champs manquants que l'annotation manuelle capture sans peine.
8. Le **seuil devra être réévalué** sur les 150 annonces traduites, puis sur de vraies transcriptions.
