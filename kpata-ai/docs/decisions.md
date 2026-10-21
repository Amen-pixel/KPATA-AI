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
