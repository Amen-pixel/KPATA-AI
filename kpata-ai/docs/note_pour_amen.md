# Note pour Amen — ajouter FLEURS à la collecte

**De** : Zozerigué
**Date** : 21 octobre 2026
**Objet** : proposition d'ajouter le corpus FLEURS à ta collecte Common Voice

Salut Amen,

Je ne touche pas à ta collecte, c'est ton périmètre. Je te propose seulement
d'ajouter une source, et je te dis pourquoi.

## La proposition

Ajouter **FLEURS** (Google) à côté de Common Voice, pour le Yorùbá et le Hausa.

- Fiche : https://huggingface.co/datasets/google/fleurs
- Codes de langue : `yo_ng` (Yorùbá) et `ha_ng` (Hausa)
- Contenu : des phrases lues à voix haute, avec leur transcription, déjà
  découpées en jeux d'entraînement, de validation et de test
- Licence : **CC-BY 4.0** — plus permissive que les modèles qu'on utilise, qui
  sont en CC-BY-NC

## Pourquoi, en deux phrases

Comme on n'a trouvé aucun locuteur, **tous nos audios en Yorùbá et en Hausa
seront des voix de synthèse** (voir D-010), et ces voix sont trop propres pour
mesurer honnêtement une transcription : Common Voice et FLEURS sont les
**seules voix réelles** dont on disposera.

Et comme la synthèse ne produit **qu'une seule voix par langue**, les
séparations par locuteur exigées au §6 du cahier des charges sont impossibles
sur nos données : elles n'ont de sens que sur ces corpus réels, où plusieurs
personnes différentes parlent.

## Ce que ça change pour toi

Pas grand-chose, je pense : FLEURS se charge comme Common Voice, et il est déjà
découpé, donc tu n'as pas de split à faire. Deux points d'attention quand même :

- vérifier que les métadonnées de locuteur sont exploitables pour nos splits —
  sur FLEURS, c'est moins détaillé que sur Common Voice ;
- noter la licence dans ton tableau de référence : CC-BY 4.0 demande de citer
  la source.

## Pour information

J'ai commencé `docs/fiche_donnees.md`, qui recense chaque source avec son
volume, sa licence et ses limites. J'y ai déjà mis une ligne pour Common Voice
et une pour FLEURS, mais **les volumes sont vides** : c'est à toi de les
remplir quand tu auras collecté. Dis-moi si tu préfères que ces deux lignes
vivent dans ton tableau de référence plutôt que dans ma fiche, pour éviter
qu'on tienne deux fois la même information.

Un point qui te concerne directement : les modèles que j'utilise (NLLB-200 pour
la traduction, MMS-TTS pour la synthèse) sont tous deux en **CC-BY-NC 4.0**,
donc **non commercial**. C'est acceptable pour un projet d'école, mais ça
interdit toute exploitation commerciale de Kpata AI entraîné sur ces données.
Le cahier des charges demande de vérifier les licences : c'est signalé dans ma
fiche, et il faudrait que l'encadrement soit au courant.

Merci,
Zozerigué
