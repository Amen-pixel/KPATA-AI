# Décisions du projet Kpata AI

Toute décision de conception est notée ici : la date, la décision, la raison, et
le statut. Statuts possibles : **proposé** (en attente de l'équipe) ou
**validé par l'équipe**.

Rappel de la règle d'or du cahier des charges : une affiche avec un prix, une
date, un numéro ou un lieu faux est un échec, même si elle est belle. En cas de
doute, le code renvoie `None` et c'est la validation qui refuse.

---

## D-001 — Numéro à 8 chiffres sans indicatif : le Bénin par défaut

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche A1)
- **Statut** : proposé
- **Décision** : `normaliser_telephone` accepte un paramètre optionnel
  `pays`. Un numéro de 8 chiffres sans indicatif est traité comme un ancien
  numéro béninois (on ajoute le `01` de tête), sauf si `pays="niger"` est passé.
  `normaliser_brief` passe `pays="niger"` quand le lieu du brief contient une
  ville clairement nigérienne : Niamey, Zinder, Maradi, Tahoua, Agadez, Dosso.
- **Raison** : 8 chiffres sans indicatif est réellement ambigu — le Bénin
  (ancien format) et le Niger ont tous deux des numéros à 8 chiffres. Garder le
  Bénin par défaut ne casse aucun des 67 tests existants, et le lieu du brief
  donne l'information manquante quand elle est disponible.
- **Limite connue** : si le commerçant est au Niger mais que son lieu n'est pas
  dans la liste des six villes (un village, un quartier), son numéro à 8
  chiffres sera préfixé `+229` à tort. Le numéro reste joignable sous sa forme
  nationale mais l'indicatif est faux. Deux pistes pour la Phase 1 : étendre la
  liste des villes, ou demander le pays au commerçant quand le numéro est
  ambigu. À trancher par l'équipe.

## D-002 — Un nombre seul n'est un prix que dans un champ de montant

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche A2)
- **Statut** : proposé
- **Décision** : `normaliser_prix` accepte un paramètre optionnel `champ`. Un
  nombre seul (`"3000"`, sans unité) n'est accepté comme prix que si
  `champ="price"` ou `champ="promotion"`. Dans un texte libre, il est refusé.
- **Raison** : dans une transcription, un nombre seul peut être un numéro de
  téléphone, une adresse ou une quantité. Afficher « 3000 F » sur une affiche
  alors que le commerçant donnait un numéro serait exactement l'échec que la
  règle d'or interdit. Quand la valeur vient du champ `price`, l'annotateur a
  déjà fait le travail d'interprétation : on peut lui faire confiance.
- **Conséquence** : un nombre seul n'a pas de devise. `detecter_devise("3000")`
  renvoie `None` et le champ `currency` du brief reste vide. On n'invente pas
  une devise.

## D-003 — Nouveau champ `currency` dans le brief

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche A2)
- **Statut** : proposé
- **Décision** : ajout du champ `currency` au schéma du brief. Valeurs
  possibles : `"XOF"` (franc CFA), `"NGN"` (naira), ou `None`. Il est déduit du
  prix ou de la réduction par `normaliser_brief`, jamais inventé, et n'écrase
  pas une devise déjà renseignée. Poids 1 dans le score C, obligatoire pour
  aucune intention.
- **Raison** : le projet couvre le Bénin (franc CFA), le Nigeria (naira) et le
  Niger (franc CFA). « 5000 » n'a pas le même sens dans les deux devises :
  afficher un prix sans sa devise est une information incomplète, donc
  trompeuse. Les réductions en montant gardent le symbole : `-10000 F` ou
  `-10000 ₦`.
- **À trancher** : faut-il rendre `currency` obligatoire dès qu'un `price` est
  présent ? Ce serait cohérent avec la règle d'or, mais cela bloquerait les
  briefs où le prix est un nombre seul. Proposition : non obligatoire en
  Phase 0, à réévaluer en Phase 1.

## D-004 — Les périodes de dates remplissent le début ET la fin

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche A3)
- **Statut** : proposé
- **Décision** : nouvelle fonction `extraire_periode(texte)` qui renvoie un
  couple `(début, fin)`. `normaliser_date` renvoie désormais le début de la
  période et non la dernière date trouvée. Dans `normaliser_brief`, une période
  dans `start_date` remplit aussi `end_date`, sans écraser une date de fin déjà
  renseignée. Un jour sans mois suivi de « au \<jour\> \<mois\> » prend le mois
  de la deuxième date : « du 28 octobre au 3 novembre » est correctement lu.
- **Raison** : « du 15 au 20 octobre » donnait « 20 octobre » comme date de
  début. Une affiche annonçant le début d'une promotion le jour de sa fin est
  une information fausse — exactement ce que la règle d'or interdit.
- **Note** : si une seule des deux bornes est valide (« du 28 au 30 février »),
  on ne garde que la borne sûre et la fin reste `None`. On ne garde jamais une
  date qui n'existe pas.

## D-005 — Poids revus selon le QA Agent ; seuil proposé à 0,6

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche B)
- **Statut** : proposé
- **Décision appliquée** : les poids suivent la criticité pour le QA Agent
  (cahier §12) et non la place sur l'affiche. `location` passe de 2 à 3 (le QA
  vérifie « lieu exact », et le lieu est obligatoire pour les sept intentions) ;
  `business_name` passe de 2 à 1 (nom propre fragile à l'ASR, non vérifié par
  le QA, `business_type` suffit à rédiger l'affiche).
- **Décision proposée, NON appliquée** : faire passer `SEUIL` de 0,5 à 0,6. La
  constante `SEUIL` reste à 0,5 dans le code ; la valeur proposée est exposée
  sous le nom `SEUIL_PROPOSE` pour pouvoir être testée sans changer le
  comportement du système.
- **Raison** : mesures sur les 20 annonces de `briefs_fr.json` (détail au §5 de
  `schema_annonce.md`). Aucun seuil testé ne produit de faux positif, avec aucun
  barème : le seuil ne protège donc pas de la règle d'or, ce sont les champs
  obligatoires et la validation qui le font. Monter le seuil ne peut que
  refuser des annonces légitimes. Avec les poids d'origine, 0,6 bloquait quatre
  annonces complètes et publiables ; avec le nouveau barème, 0,6 garde 20/20
  d'accords. C'est la seule combinaison qui ajoute une marge de sécurité sans
  rien casser.
- **Réserve** : 20 annonces sont trop peu pour trancher. À réexaminer sur les
  150 annonces de la tâche D, puis sur de vraies transcriptions en Phase 1,
  où l'ASR fera manquer des champs que l'annotation manuelle capture sans peine.

## D-006 — Trois écarts de nommage par rapport au cahier des charges

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche B)
- **Statut** : proposé
- **Décision** : le schéma s'écarte du §6 du cahier sur trois points, tous
  documentés au §2 de `schema_annonce.md`.
  1. Le champ `dates` du §6 est éclaté en `start_date` et `end_date`. L'exemple
     du §4 utilise lui-même les deux champs séparés, et le §12 demande au QA de
     vérifier que « les dates sont exactes » : c'est impossible avec un champ
     unique.
  2. Le `media` du §4 garde le nom `requested_media` du §6. Le cahier emploie
     les deux ; on retient celui du schéma de dataset, car c'est une demande de
     l'utilisateur et non le support finalement produit.
  3. `audio_path` et `transcript` (§6) ne sont pas des slots du brief mais des
     champs d'enveloppe de l'annonce. Ils sont décrits séparément au §1 du
     document. `audio_path` reste vide en Phase 0 (annonces écrites à la main)
     et devient obligatoire en Phase 1.
- **Raison** : le cahier des charges prime, mais il se contredit lui-même entre
  §4 et §6 sur les dates et le nom du support. Le choix retenu est celui qui
  rend la vérification du QA Agent possible.

## D-007 — Informations sous-entendues : fêtes à date fixe seulement

- **Date** : 21 octobre 2026
- **Auteur** : Zozerigué (tâche C)
- **Statut** : proposé
- **Décision** : on n'écrit une information déduite que si elle est certaine,
  vérifiable et indépendante de la personne.
  - **Fêtes à date fixe : on écrit la date.** Saint-Valentin (14 février), Noël
    (25 décembre), Nouvel An (1 janvier), fête du travail (1 mai).
  - **Fêtes mobiles : `null`, toujours.** Pâques, Tabaski (Aïd el-Kébir),
    Ramadan, Aïd el-Fitr.
  - **Tout le reste reste `null`** : pas de ville ajoutée à un nom de marché,
    pas de devise déduite du pays, pas de prix déduit de « prix cassés », pas de
    date calendaire déduite de « ce week-end ».
- **Raison** : une date de calendrier publique est identique chaque année, donc
  l'écrire n'est pas un pari. Une fête mobile change de date : écrire une date
  serait inventer une information, ce que la règle d'or interdit. La frontière
  retenue est donc « est-ce vérifiable sans demander à la personne ? ».
- **Conséquence sur l'existant** : l'annonce 16 de `briefs_fr.json`
  (Saint-Valentin) était classée `evenement`. Elle passe en `promotion` : une
  promotion à l'occasion d'une fête annonce la réduction, pas la fête. La date
  du 14 février est conservée, conformément à la règle ci-dessus. Corrigé dans
  `scripts/generer_briefs.py`.
- **À trancher** : faut-il une liste de fêtes dans le code, pour que la
  normalisation fasse ce travail automatiquement plutôt que l'annotateur ? Cela
  relève de la Phase 2 (extraction assistée par modèle).
