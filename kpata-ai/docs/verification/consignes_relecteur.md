# Consignes pour le relecteur — Kpata AI

Merci de nous aider. Ce travail prend **environ une heure** pour 20 phrases.

## Ce que nous faisons

Nous construisons un assistant vocal pour les petits commerçants d'Afrique de
l'Ouest. Un commerçant parle dans sa langue, et l'outil fabrique une affiche
publicitaire pour lui.

Nous avons traduit des annonces du français vers le Yorùbá (ou le Hausa) avec
un **outil automatique**. Personne dans notre équipe ne parle ces langues, nous
ne pouvons donc pas juger du résultat. C'est pour cela que nous avons besoin de
vous.

## Ce que vous recevez

Un fichier avec 20 lignes. Chaque ligne contient :

- `texte_fr` : la phrase d'origine, en français ;
- `traduction` : ce que l'outil a produit dans votre langue.

Et quatre colonnes **vides**, que vous remplissez.

## Les 3 choses à vérifier

### 1. `sens_correct` — écrivez **oui** ou **non**

La traduction dit-elle la même chose que le français ? Nous ne demandons pas si
la phrase est jolie, seulement si **le sens est le bon**.

- Phrase maladroite mais compréhensible, qui dit la bonne chose → **oui**
- Phrase qui dit autre chose, ou qu'on ne comprend pas → **non**

### 2. `infos_critiques_correctes` — écrivez **oui** ou **non**

**C'est la colonne la plus importante pour nous.** Vérifiez que ces informations
sont **exactement** les mêmes dans les deux textes :

- les **prix** et les **réductions** (pourcentages, montants) ;
- les **dates** et les **jours** ;
- les **numéros de téléphone**, chiffre par chiffre ;
- les **noms de lieux** et les **noms de commerces**.

Si une seule de ces informations a changé — un chiffre différent, une ville
disparue, une date décalée — répondez **non**, même si le reste de la phrase est
parfait.

Pour nous, une affiche avec un prix ou un numéro faux est un **échec complet**,
même si elle est belle.

### 3. `naturel` — donnez une note **de 1 à 5**

Un commerçant de votre région parlerait-il comme ça ?

| Note | Ce que ça veut dire |
| --- | --- |
| 1 | Incompréhensible, ou ce n'est pas vraiment ma langue |
| 2 | On devine le sens, mais c'est très mal dit |
| 3 | Compréhensible, mais on sent tout de suite une machine |
| 4 | Correct, un peu scolaire |
| 5 | Naturel, un commerçant pourrait dire ça |

### `commentaire` — libre, et facultatif

Si une traduction vous semble étrange, dites-nous pourquoi en quelques mots.
C'est très utile. Vous pouvez écrire en français ou en anglais.

## Comment rendre

Remplissez le fichier et renvoyez-le tel quel. **Ne corrigez pas les
traductions** : nous avons besoin de savoir ce que l'outil produit, pas d'avoir
de bonnes traductions. Si vous voulez proposer une meilleure formulation,
mettez-la dans le commentaire.

Si une ligne vous laisse hésitant, laissez-la vide plutôt que de deviner : une
case vide ne compte pas dans nos calculs.

---

# Instructions for the reviewer — Kpata AI (English)

Thank you for helping us. This task takes **about one hour** for 20 sentences.

## What we are doing

We are building a voice assistant for small traders in West Africa. A trader
speaks in their own language, and the tool creates an advertising poster for
them.

We translated trader announcements from French into Yorùbá (or Hausa) using a
**machine translation tool**. Nobody on our team speaks these languages, so we
cannot judge the output ourselves. That is why we need you.

## What you receive

A file with 20 rows. Each row contains:

- `texte_fr`: the original sentence, in French;
- `traduction`: what the tool produced in your language.

Plus four **empty** columns for you to fill in.

## The 3 things to check

### 1. `sens_correct` — write **oui** (yes) or **non** (no)

Does the translation say the same thing as the French? We are not asking whether
the sentence is elegant, only whether **the meaning is right**.

- Awkward but understandable, and says the right thing → **oui**
- Says something different, or is incomprehensible → **non**

### 2. `infos_critiques_correctes` — write **oui** or **non**

**This is the most important column for us.** Check that these details are
**exactly** the same in both texts:

- **prices** and **discounts** (percentages, amounts);
- **dates** and **days of the week**;
- **phone numbers**, digit by digit;
- **place names** and **business names**.

If even one of these has changed — a different digit, a missing city, a shifted
date — answer **non**, even if the rest of the sentence is perfect.

For us, a poster with a wrong price or phone number is a **complete failure**,
no matter how good it looks.

### 3. `naturel` — give a score **from 1 to 5**

Would a trader from your region actually speak this way?

| Score | Meaning |
| --- | --- |
| 1 | Incomprehensible, or not really my language |
| 2 | Meaning can be guessed, but very badly phrased |
| 3 | Understandable, but clearly machine-made |
| 4 | Correct, slightly bookish |
| 5 | Natural, a trader could say this |

### `commentaire` — free text, optional

If a translation seems odd, tell us why in a few words. This is very useful.
You may write in English or French.

## How to return it

Fill in the file and send it back as is. **Please do not fix the
translations** — we need to know what the tool produces, not to obtain good
translations. If you want to suggest a better phrasing, put it in the comment
column.

If a row leaves you unsure, leave it blank rather than guessing: blank cells are
excluded from our calculations.
