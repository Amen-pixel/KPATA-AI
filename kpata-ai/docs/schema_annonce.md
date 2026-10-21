# Schéma de l'annonce Kpata AI

Document de référence de la Phase 0. Il fixe les champs d'un brief, leur forme
normalisée, leur poids dans le score de complétude et les conditions du feu
vert. Les trois membres de l'équipe s'appuient sur ce document.

Sources : cahier des charges §4 (objet structuré), §5 (score C), §6 (schéma
minimal), §7.1 (intentions), §7.2 (champs prioritaires), §12 (QA Agent).

> **Règle d'or (cahier §7.2).** Une affiche visuellement réussie avec un prix ou
> un numéro faux est un échec du système. Aucune information ne doit être
> inventée. En cas de doute, le code renvoie `None` et la validation refuse.

---

## 1. Deux niveaux : l'enveloppe et les slots

Le cahier §6 liste `audio_path, language, transcript, intent, business_type,
product, promotion, price, dates, location, phone, tone, requested_media`. Ces
champs ne sont pas tous de même nature. On distingue donc deux niveaux.

**L'enveloppe** décrit l'annonce en tant que donnée du dataset :

| Champ | Définition | Exemple |
| --- | --- | --- |
| `id` | numéro de l'annonce dans le lot | `1` |
| `audio_path` | chemin de la note vocale, relatif à `data/audio/` | `yoruba_L03_012.wav` |
| `transcript` | ce que la personne a dit, transcrit | `"J'ai une boutique…"` |
| `source` | origine du texte | `ecrit_equipe`, `natif`, `traduit_verifie`, `traduit_non_verifie`, `a_traduire` |
| `annotateur` | initiales de la personne qui a annoté | `TZ` |
| `pret_attendu` | feu vert attendu, pour tester le moteur | `true` |
| `piege` | la difficulté que l'annonce teste | `"numéro invalide"` |

**Les slots** forment le brief proprement dit : c'est ce que le moteur de
complétude évalue et ce que les agents de génération consomment. C'est la liste
`CHAMPS` de `src/kpata/brief.py`, détaillée ci-dessous.

En Phase 0 les annonces sont écrites à la main : `audio_path` est vide. Il
devient obligatoire en Phase 1, quand la Kpata Data Factory traitera de vrais
enregistrements.

## 2. Les champs du brief (slots)

Poids = contribution au score C. « Obligatoire pour » = intentions qui ne
peuvent pas obtenir le feu vert sans ce champ. `A ou B` signifie « au moins un
des deux ».

| Champ | Définition | Forme normalisée | Poids | Obligatoire pour |
| --- | --- | --- | --- | --- |
| `language` | langue de la note vocale | `yoruba`, `hausa`, `francais` | — | toutes |
| `intent` | ce que la personne veut annoncer | une des 7 intentions du §3 | — | toutes |
| `product` | le produit ou le service dont on parle | texte, 2 caractères minimum | 3 | promotion, offre_limitee, lancement, restock, annonce_service |
| `phone` | numéro de contact | `+229` / `+234` / `+227` suivi du numéro national | 3 | toutes |
| `promotion` | la réduction annoncée | `-20 %` ou `-10000 F` ou `-10000 ₦` | 3 | promotion, offre_limitee (`promotion ou price`) |
| `price` | un prix affiché | entier positif, ex. `2500` | 3 | promotion, offre_limitee (`promotion ou price`) |
| `location` | où se trouve le commerce | texte, 3 caractères minimum | 3 | toutes |
| `start_date` | début de l'offre | `vendredi`, `15 octobre`, `demain`, `week-end` | 2 | evenement, offre_limitee (`start_date ou end_date`) |
| `end_date` | fin de l'offre | même forme que `start_date` | 1 | offre_limitee (`start_date ou end_date`) |
| `business_name` | nom propre du commerce | texte, 2 caractères minimum | 1 | ouverture (`business_name ou business_type`) |
| `business_type` | nature du commerce | texte, 3 caractères minimum | 1 | ouverture (`business_name ou business_type`) |
| `currency` | devise du prix | `XOF` (franc CFA) ou `NGN` (naira) | 1 | aucune |
| `tone` | ton demandé pour l'affiche | `chaleureux`, `festif`, `professionnel`, `luxe` | 1 | aucune |
| `requested_media` | support demandé | `poster_whatsapp`, `poster_portrait`, `statut_whatsapp`, `texte_publication` | 1 | aucune |

`language` et `intent` n'ont pas de poids : ils ne sont pas des informations à
afficher mais les conditions d'entrée du moteur. Sans eux, le score C n'a pas de
sens, puisque la liste des champs obligatoires dépend de l'intention.

### Écarts assumés par rapport au cahier des charges

Trois différences, toutes volontaires. Elles doivent être validées par l'équipe.

1. **`dates` est éclaté en `start_date` et `end_date`.** Le cahier §6 écrit un
   seul champ `dates`, mais l'exemple du §4 utilise bien `start_date` et
   `end_date` séparés. Le §12 demande au QA Agent de vérifier que les « dates
   sont exactes » : deux champs distincts le permettent, un champ unique non.
2. **`media` du §4 s'appelle `requested_media`.** Le cahier emploie les deux
   noms (§4 `media`, §6 `requested_media`). Le code garde `requested_media`,
   celui du schéma de dataset, parce que c'est une demande de l'utilisateur et
   non le support finalement produit.
3. **`currency` est un ajout.** Le cahier ne le prévoit pas. Il devient
   nécessaire dès qu'on couvre le Nigeria : « 5000 » ne veut pas dire la même
   chose en franc CFA et en naira, et afficher un prix sans sa devise est une
   information trompeuse au sens de la règle d'or. Voir `decisions.md` (D-003).

## 3. Les sept intentions

Liste fixée par le cahier §7.1. Une annonce a exactement une intention.

| Intention | Définition |
| --- | --- |
| `promotion` | Un prix est baissé sur un produit déjà vendu habituellement. |
| `offre_limitee` | Une promotion valable sur une période explicitement bornée, après quoi elle s'arrête. |
| `lancement` | Un produit ou un service nouveau entre au catalogue d'un commerce qui existe déjà. |
| `ouverture` | Le commerce lui-même ouvre ses portes pour la première fois, ou ouvre un nouveau point de vente. |
| `evenement` | Une manifestation datée : journée portes ouvertes, fête, braderie, défilé. |
| `restock` | Un produit habituel est de nouveau disponible après une rupture ou un nouvel arrivage. |
| `annonce_service` | Une présentation d'activité sans baisse de prix ni nouveauté : on fait savoir ce qu'on propose. |

Les règles pour distinguer les cas proches (`promotion` / `offre_limitee`,
`ouverture` / `lancement`, `restock` / `annonce_service`) sont dans
`guide_annotation.md`.

## 4. La règle du feu vert

Le feu vert autorise le Campaign Orchestrator (cahier §4) à lancer la
génération. Trois conditions, toutes nécessaires :

1. **L'intention est connue.** `intent` fait partie des sept.
2. **Aucun champ obligatoire ne manque** pour cette intention
   (`champs_manquants(brief)` est vide). Le téléphone et le lieu sont
   obligatoires pour toutes les intentions : le cahier §4 donne précisément
   l'exemple d'un brief complet sauf le téléphone, et exige que le système ne
   l'invente pas mais pose la question.
3. **Le score de complétude atteint le seuil** : `C >= SEUIL`.

Si une condition échoue, le système **ne génère pas** : il demande l'information
manquante à la personne, puis reprend le workflow là où il s'était arrêté.

À cela s'ajoute la validation, qui est une étape distincte : un champ **présent
mais incorrect** (`150 %` de réduction, numéro à 5 chiffres, 30 février) est
refusé par `valider_brief` même si tous les champs obligatoires sont là. Un
champ absent n'est pas invalide — c'est le rôle du moteur de complétude de le
signaler.

### Le score de complétude C

Formule du cahier §5 :

$$C = \frac{\sum_i w_i \cdot \mathbf{1}(\text{field}_i \text{ présent})}{\sum_i w_i}$$

Concrètement : on additionne les poids des champs utiles **qui sont remplis**, on
divise par la somme des poids de **tous** les champs utiles. Les champs utiles
sont les champs obligatoires de l'intention, plus les champs souhaités. Un champ
qui ne concerne pas l'intention ne compte ni au numérateur ni au dénominateur.

Pour un groupe `A ou B`, le groupe compte une seule fois, avec le poids le plus
élevé des deux, et il est satisfait dès que l'un des deux champs est rempli.

C mesure la **richesse** du brief, pas sa justesse. Un brief peut avoir un C
élevé et contenir un prix faux : c'est la validation et le QA Agent (§12) qui
traitent la justesse. Il ne faut donc pas attendre du seuil qu'il protège de la
règle d'or.

## 5. Justification des poids et du seuil

### Les poids

Le principe retenu : **le poids d'un champ suit sa criticité pour le QA Agent**,
pas sa simple présence sur l'affiche. Le §12 énumère ce que le QA vérifie — prix,
réduction, dates, téléphone, lieu. Ce sont ces champs qui font échouer une
campagne quand ils sont faux ou absents. Les sept champs prioritaires du §7.2
(prix, réduction, date, numéro, localisation, produit, nom commercial) servent de
seconde référence.

Trois barèmes ont été testés sur les 20 annonces de `briefs_fr.json`. Le test
compare le feu vert calculé au `pret_attendu` annoté.

| Barème | C moyen | Accords à 0,5 | Accords à 0,6 | Accords à 0,7 |
| --- | --- | --- | --- | --- |
| A — poids d'origine (`location` 2, `business_name` 2) | 0,63 | 20/20 | 16/20 | 13/20 |
| B — §7.2 strict (les 7 prioritaires à 3) | 0,61 | 20/20 | 14/20 | 13/20 |
| **C — `location` 3, `business_name` 1** | 0,68 | **20/20** | **20/20** | 13/20 |

**Barème retenu : C.** Deux changements par rapport à l'origine :

- `location` passe de 2 à 3. Le lieu est vérifié par le QA Agent (§12 « lieu
  exact ») et il est obligatoire pour les sept intentions : une affiche sans lieu
  n'est pas actionnable. Il mérite le même poids que le téléphone.
- `business_name` passe de 2 à 1. C'est un nom propre, donc une information
  fragile à l'ASR, et le §12 ne le vérifie pas. Il est souvent absent des notes
  vocales réelles sans que la campagne en souffre : `business_type` suffit à
  rédiger l'affiche.

### Le seuil

Le seuil d'origine est 0,5. Les mesures montrent qu'il n'y a **aucun faux
positif à aucun seuil testé, avec aucun barème** : jamais une annonce incomplète
n'obtient le feu vert à cause d'un seuil trop bas. Les quatre refus attendus
(annonces 4, 11, 13, 20) le sont pour champ obligatoire manquant, et deux autres
(14, 15) pour valeur invalide. Le seuil ne décide dans aucun cas.

Autrement dit : **monter le seuil ne rend pas le système plus sûr, il bloque des
annonces légitimes.** Avec le barème d'origine, un seuil de 0,6 refuse quatre
annonces complètes et publiables (6, 7, 9, 12) — par exemple un restock avec
produit, lieu et téléphone, qui n'a aucune raison d'être bloqué.

Le barème C change la donne : il garde 20/20 à 0,5 **et** à 0,6.

> **Proposition — à valider par l'équipe : seuil 0,6 avec le barème C.**
>
> Raison : c'est la seule combinaison qui offre une marge de sécurité sans
> refuser une seule annonce légitime. Un brief qui n'atteint pas 0,6 est pauvre
> au point qu'une question de clarification est plus utile qu'une affiche.
>
> Réserve : 20 annonces sont trop peu pour trancher définitivement. La décision
> doit être réexaminée sur les 150 annonces de la tâche D, puis sur de vraies
> transcriptions en Phase 1, où l'ASR fera manquer des champs que l'annotation
> manuelle capture sans peine.

Le code et ce document doivent rester alignés : `tests/test_schema_aligne.py`
vérifie cette correspondance et échoue si l'un des deux change sans l'autre.

## 6. Questions ouvertes pour l'équipe

1. **Seuil et poids** : valider le barème C et le seuil 0,6, ou garder 0,5 en
   attendant les 150 annonces de la tâche D ?
2. **`currency` obligatoire avec un prix ?** Cohérent avec la règle d'or, mais
   cela bloquerait les briefs dont le prix est un nombre seul, sans unité. Non
   obligatoire en Phase 0 ; à revoir en Phase 1 (D-003).
3. **Plusieurs produits dans une annonce.** Les slots n'acceptent aujourd'hui
   qu'un seul `product`. Faut-il une liste ? Règle provisoire du guide
   d'annotation : on retient le produit mis en avant. À trancher avant la
   Phase 2, car cela change le format d'extraction.
4. **Numéro à 8 chiffres ambigu** entre le Bénin et le Niger quand le lieu
   n'est pas une des six villes nigériennes connues (D-001). Étendre la liste,
   ou demander le pays à la personne ?
5. **`tone` et `requested_media`** ne sont presque jamais exprimés dans une note
   vocale. Faut-il une valeur par défaut (`chaleureux`, `poster_whatsapp`) ou
   les laisser vides ? Les laisser vides coûte du score C sans gain
   d'information ; les remplir d'office s'approche d'inventer. Proposition :
   les retirer du dénominateur de C tant qu'ils ne sont pas demandés
   explicitement — décision pour Eudes, qui tient la logique de `completude()`.
