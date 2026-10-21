# Guide d'annotation Kpata AI

Ce guide sert à ce que les trois membres de l'équipe annotent une annonce
exactement de la même façon. Quand une situation n'est pas couverte ici, on ne
devine pas : on en discute, on tranche, et la règle est ajoutée au guide et à
`decisions.md`.

Le schéma des champs est dans `schema_annonce.md`. Ce guide dit comment le
remplir.

> **Règle d'or (cahier §7.2).** Une affiche avec un prix, une date, un numéro ou
> un lieu faux est un échec, même si elle est belle. On n'écrit jamais dans un
> slot une information que la personne n'a pas donnée. Dans le doute : `null`.

---

## 1. Le format d'une annonce annotée

Une annonce est un objet JSON. Les fichiers sont dans `data/briefs/`.

| Clé | Rôle | Valeurs |
| --- | --- | --- |
| `id` | numéro dans le lot, unique | entier |
| `transcript` | ce que la personne a dit, mot pour mot | texte |
| `slots` | les champs extraits, normalisés | objet (voir `schema_annonce.md`) |
| `pret_attendu` | le feu vert que le moteur devrait donner | `true` / `false` |
| `piege` | la difficulté testée, en une phrase | texte, vide si aucune |
| `source` | d'où vient le texte | voir ci-dessous |
| `annotateur` | initiales de qui a annoté | `AQ`, `TZ`, `ME` |

Valeurs de `source` :

| Valeur | Signification |
| --- | --- |
| `ecrit_equipe` | texte écrit par l'équipe, en français |
| `natif` | transcription d'une personne qui parle la langue |
| `traduit_verifie` | traduit, puis relu par une personne qui parle la langue |
| `traduit_non_verifie` | traduction automatique, pas encore relue |
| `a_traduire` | texte français en attente de traduction par un locuteur |

`traduit_non_verifie` ne sert **jamais** à mesurer une performance : ces
annonces sont exclues des jeux de validation et de test tant qu'un locuteur ne
les a pas relues.

### Exemple complet

```json
{
  "id": 7,
  "transcript": "J'ai reçu du wax à Dantokpa, 6000 F le pagne. Appelez le 0196000000.",
  "slots": {
    "language": "francais",
    "intent": "restock",
    "business_name": null,
    "business_type": "vendeuse de tissus",
    "product": "wax",
    "promotion": null,
    "price": "6000 F",
    "currency": null,
    "start_date": null,
    "end_date": null,
    "location": "Dantokpa",
    "phone": "0196000000",
    "tone": null,
    "requested_media": null
  },
  "pret_attendu": true,
  "piege": "",
  "source": "ecrit_equipe",
  "annotateur": "TZ"
}
```

Remarques sur cet exemple :

- `business_name` est `null` : la personne n'a pas donné le nom de son commerce.
  `business_type` est déduit de « j'ai reçu du wax » — c'est une description, pas
  un nom propre, donc c'est permis.
- `price` garde son unité (`"6000 F"`). C'est `normaliser_prix` qui en fait
  l'entier `6000`, et `detecter_devise` qui en déduit `XOF`. **On n'écrit pas la
  valeur normalisée à la main** : on écrit ce que la personne a dit, le code
  normalise. C'est ainsi qu'on teste la normalisation.
- `currency` est `null` dans l'annotation : il est rempli par le code.

## 2. Les sept intentions

Une annonce a **exactement une** intention. On choisit celle qui répond à la
question : *qu'est-ce que la personne veut faire savoir en premier ?*

### `promotion`
Un prix est baissé sur un produit déjà vendu habituellement.
- « Réduction de 20 % sur les chaussures vendredi et samedi. »
- « Moins 30 % sur la coiffure cette semaine. »

### `offre_limitee`
Une promotion dont la **fin est explicitement annoncée**. C'est la rareté qui est
le message.
- « Sacs à moins 40 % **samedi seulement**. »
- « Poulet braisé à 2 500 F **jeudi et vendredi uniquement**. »

> **`promotion` ou `offre_limitee` ?** On met `offre_limitee` seulement si la
> personne **borne la durée** avec un mot de limitation : « seulement »,
> « uniquement », « jusqu'à », « les 3 premiers jours », « du … au … ». Une
> promotion qui a des dates mais sans mot de limitation reste une `promotion` :
> « moins 20 % vendredi et samedi » est une `promotion`, pas une
> `offre_limitee`. En cas d'hésitation, `promotion` — c'est le cas général.

### `lancement`
Un produit ou service **nouveau** entre au catalogue d'un commerce qui **existe
déjà**.
- « Je lance mon jus de bissap, 500 F le verre. »
- « Nouveau service de livraison à domicile dans ma boutique. »

### `ouverture`
Le **commerce lui-même** ouvre pour la première fois, ou ouvre un nouveau point
de vente.
- « Mon salon de coiffure ouvre samedi à Cotonou. »
- « Ma boulangerie ouvre lundi à Bohicon. »

> **`ouverture` ou `lancement` ?** On regarde **ce qui est neuf**. Si c'est le
> commerce (ou un nouveau local) : `ouverture`. Si c'est un produit dans un
> commerce qui tourne déjà : `lancement`. Test rapide : « ouvre », « ouverture »,
> « j'inaugure » → `ouverture`. « Je lance », « nouveau produit », « désormais
> disponible chez moi » → `lancement`.

### `evenement`
Une **manifestation datée** est l'objet de l'annonce : journée portes ouvertes,
braderie, défilé, fête organisée par le commerce.
- « Journée portes ouvertes samedi dans mon centre de formation. »
- « Grande braderie dimanche au marché. »

> **Attention.** Une promotion *à l'occasion* d'une fête n'est pas un
> `evenement`. « Pour la Saint-Valentin, moins 20 % sur les bouquets » est une
> `promotion` : ce qui est annoncé est la réduction, la fête n'est que le
> prétexte. On met `evenement` seulement quand la manifestation **est**
> l'information principale.

### `restock`
Un produit habituel est **de nouveau disponible** après une rupture, ou un
nouvel arrivage est arrivé.
- « Nouvel arrivage de téléphones dans ma boutique. »
- « J'ai reçu du wax à Dantokpa. »

### `annonce_service`
On fait savoir ce qu'on propose. **Ni baisse de prix, ni nouveauté, ni
arrivage.**
- « Électricien à Cotonou, j'installe et je répare chez vous. »
- « Mon cybercafé fait la photocopie à 25 F la page. »

> **`restock` ou `annonce_service` ?** On cherche l'idée de **retour en stock**
> ou d'**arrivage** : « j'ai reçu », « nouvel arrivage », « c'est revenu »,
> « disponible à nouveau » → `restock`. Une simple présentation de l'activité,
> même avec un prix, → `annonce_service`.

## 3. Comment remplir chaque champ

Principe général : **on écrit ce que la personne a dit**, dans la forme la plus
proche possible, et on laisse le code normaliser. On écrit `null` dès que
l'information n'est pas dans le `transcript`.

| Champ | Ce qu'on écrit | `null` quand |
| --- | --- | --- |
| `language` | `francais`, `yoruba` ou `hausa` | jamais |
| `intent` | une des sept intentions | jamais — si on ne sait pas, on en discute |
| `product` | le produit ou service, au plus proche des mots dits | aucun produit n'est nommé |
| `business_name` | le **nom propre** du commerce (« Chez Tanti Rose ») | aucun nom propre n'est dit |
| `business_type` | la nature du commerce, même déduite de l'activité | on ne peut pas dire de quel commerce il s'agit |
| `promotion` | la réduction telle que dite : `"20%"`, `"10 000 F"` | aucune réduction annoncée |
| `price` | le prix avec son unité : `"2 500 F"`, `"5000 naira"` | aucun prix annoncé |
| `currency` | **rien, toujours `null`** — c'est le code qui le remplit | toujours |
| `start_date` | le début tel que dit : `"vendredi"`, `"15 octobre"`, `"du 15 au 20 octobre"` | aucune date de début |
| `end_date` | la fin si elle est dite séparément | la fin n'est pas dite, ou elle est déjà dans une période écrite dans `start_date` |
| `location` | le lieu tel que dit, quartier compris : `"Cadjèhoun, Cotonou"` | aucun lieu |
| `phone` | le numéro tel que dit, espaces compris | aucun numéro |
| `tone` | un des quatre tons, **seulement si demandé** | la personne ne demande pas de ton — le cas normal |
| `requested_media` | un des quatre supports, **seulement si demandé** | la personne ne précise pas — le cas normal |

Deux pièges fréquents :

- **`business_type` est permis, `business_name` ne l'est pas.** Dire « j'ai une
  boutique de chaussures » autorise `business_type = "boutique de chaussures"` :
  c'est dans la phrase. Mais cela n'autorise aucun nom de commerce.
- **Ne jamais corriger un numéro ou un prix.** Si la personne dit « 12345 », on
  écrit `"12345"`. C'est à la validation de le refuser. Une annonce avec une
  information invalide est utile : elle teste le refus.

## 4. Les cas difficiles

### 4.1 Une information sous-entendue

**Règle : on écrit une information déduite seulement si elle est certaine,
vérifiable et indépendante de la personne. Sinon, `null`.**

Concrètement, deux familles :

**Fêtes à date fixe — on écrit la date.** Saint-Valentin → 14 février, Noël →
25 décembre, Nouvel An → 1 janvier, fête du travail → 1 mai. Ce sont des faits
de calendrier publics, identiques chaque année : il n'y a aucun risque de se
tromper, donc ce n'est pas une invention.

**Fêtes mobiles — `null`, toujours.** Pâques, Tabaski (Aïd el-Kébir), Ramadan,
Aïd el-Fitr changent de date chaque année. Écrire une date serait un pari.

- « Pour la Saint-Valentin, moins 20 % sur les bouquets »
  → `start_date = "14 février"`, `intent = "promotion"`.
- « Pour la Tabaski, moins 20 % sur les moutons »
  → `start_date = null`. L'orchestrateur demandera la date.

**Tout le reste reste `null`.** En particulier :

- Un lieu déduit du nom d'un marché : « à Dantokpa » donne
  `location = "Dantokpa"`, mais on n'ajoute pas « Cotonou » de notre tête.
- Une devise déduite du pays : jamais. C'est le code, à partir de l'unité dite.
- Un prix déduit de « pas cher », « prix cassés » : jamais.
- Une date déduite de « ce week-end » : on écrit `"week-end"` tel quel, c'est
  une valeur que le code connaît ; on ne met pas une date calendaire.

Voir `decisions.md` (D-007) pour le raisonnement complet et la liste des fêtes.

### 4.2 Plusieurs produits dans une seule annonce

**Règle : on retient le produit mis en avant** — celui qui porte le prix ou la
réduction, ou celui qui est nommé en premier si tous sont au même niveau. Les
autres restent hors des slots.

- « Chaussures et sacs à moins 30 % » → `product = "chaussures et sacs"` si
  l'offre porte sur les deux, car c'est un seul lot d'offre.
- « Promo sur les chaussures ; j'ai aussi des sacs » → `product = "chaussures"`.
  Les sacs ne sont pas dans l'offre.
- « Tout le magasin à moins 20 % » → `product = "tout le magasin"`.

Le schéma n'accepte qu'un seul `product` ; une liste est une question ouverte
(`schema_annonce.md` §6).

### 4.3 Plusieurs intentions possibles

**Règle : on garde l'intention de l'information principale**, celle que la
personne annonce en premier et qui porterait le titre de l'affiche. En cas
d'égalité réelle, cet ordre de priorité :

```
ouverture > evenement > lancement > offre_limitee > promotion > restock > annonce_service
```

Logique : un fait rare et daté (une ouverture, un événement) primé sur un fait
récurrent (une promotion, un arrivage).

- « Ma boutique ouvre samedi, et moins 20 % ce jour-là » → `ouverture`.
- « Nouvel arrivage de wax, et moins 10 % dessus » → `promotion` l'emporte sur
  `restock` : la réduction est l'argument de vente.

Toute annonce dont l'intention a demandé une discussion reçoit un `piege` qui
l'explique.

### 4.4 Un prix et une réduction en même temps

**Règle : on remplit les deux champs.** Ils ne disent pas la même chose :
`price` est le montant à payer, `promotion` est la baisse. Les deux peuvent
figurer sur l'affiche.

- « Les tresses sont à 3 000 F au lieu de 5 000 »
  → `price = "3000 F"`, `promotion = "2000 F"` (la baisse, pas l'ancien prix).
- « Moins 20 %, les chaussures sont à 8 000 F »
  → `price = "8000 F"`, `promotion = "20%"`.
- « Au lieu de 5 000 F » **sans** nouveau prix → `price = null`,
  `promotion = null`. On ne calcule rien, on ne devine pas le nouveau prix.

**On ne calcule jamais un prix à partir d'un pourcentage, ni l'inverse.** Un
calcul est une invention au sens de la règle d'or.

### 4.5 Une phrase incomplète ou hésitante

À l'oral, les gens se reprennent. **Règle : on garde le `transcript` tel quel,
hésitations comprises, et on annote la dernière valeur énoncée.**

- « C'est à 2 000… non, 2 500 F » → `transcript` garde tout,
  `price = "2 500 F"`.
- « Mon numéro c'est 0197… attendez… 0196112233 » → `phone = "0196112233"`.
- « Je fais une promo sur les… » (phrase abandonnée) → `product = null`, et le
  `piege` indique « phrase abandonnée, produit manquant ». Ces annonces sont
  précieuses : elles testent la demande de clarification.

Garder les hésitations dans le `transcript` est important : c'est ce que l'ASR
produira en Phase 1.

## 5. La double annotation

**Une annonce sur cinq est annotée par deux personnes**, indépendamment : celles
dont l'`id` est un multiple de 5. La seconde annotation est faite sans regarder
la première.

On compare ensuite champ par champ. Un désaccord se tranche ainsi :

1. **On relit le `transcript`.** La plupart des désaccords viennent d'une
   lecture rapide, pas d'une divergence de règle.
2. **On cherche la règle dans ce guide.** Si elle existe, elle décide — même si
   les deux annotateurs préféraient autre chose.
3. **Si le guide ne dit rien**, c'est un trou dans le guide, pas une erreur
   d'annotateur. On tranche à trois, on ajoute la règle à ce guide et la
   décision à `decisions.md`.
4. **Si le doute persiste** après discussion : la valeur passe à `null` et
   l'annonce reçoit un `piege` qui décrit l'ambiguïté. `null` est toujours plus
   sûr qu'une valeur inventée.

On note le taux d'accord par champ dans le bilan de phase
(`scripts/bilan_phase0.py`). Un champ dont le taux d'accord est bas signale une
règle mal écrite dans ce guide, et il faut la corriger.

## 6. Avant d'envoyer une Pull Request

- [ ] `pytest` est vert.
- [ ] Chaque annonce a un `id` unique, une `source` et un `annotateur`.
- [ ] Aucun vrai nom et aucun vrai numéro de personne. Les numéros sont
      inventés et respectent les formats du pays.
- [ ] Les valeurs des slots sont écrites comme la personne les a dites, pas
      déjà normalisées à la main.
- [ ] Chaque annonce dont `pret_attendu` est `false` a un `piege` qui explique
      pourquoi.
- [ ] Aucun fichier audio n'est ajouté à Git.
