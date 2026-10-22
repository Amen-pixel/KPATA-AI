# Génère briefs_fr.json : les annonces annotées en français
# Format et règles d'annotation : docs/guide_annotation.md
import json

from kpata.schema import nouveau_brief as s

# Lot 1 : 20 annonces écrites par Amen.
# (intent, ce que dit la personne, champs extraits, prêt attendu ?, piège)
B = [
 ("promotion", "J'ai une boutique de chaussures à Calavi. Réduction de 20% vendredi et samedi. Mon numéro c'est 0197000000.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="20%", location="Abomey-Calavi", phone="0197000000", start_date="vendredi", end_date="samedi"), True, "cas de référence du cahier des charges"),
 ("ouverture", "Mon salon de coiffure ouvre samedi à Cotonou. Les tresses sont à 3000 F. Appelez le 97 12 34 56.",
  s(business_type="salon de coiffure", product="tresses", price="3000 F", location="Cotonou", phone="97 12 34 56", start_date="samedi"), True, "ancien format à 8 chiffres"),
 ("offre_limitee", "Au restaurant à Porto-Novo, poulet braisé à 2 500 F jeudi et vendredi seulement. Numéro : +229 01 96 55 44 33.",
  s(business_type="restaurant", product="poulet braisé", price="2 500 F", location="Porto-Novo", phone="+229 01 96 55 44 33", start_date="jeudi", end_date="vendredi"), True, "prix avec espace"),
 ("promotion", "Je suis couturière à Parakou, je fais moins 15% sur les pagnes cette semaine.",
  s(business_type="couturière", product="pagnes", promotion="15%", location="Parakou"), False, "téléphone manquant"),
 ("promotion", "Ma pâtisserie à Abomey-Calavi fait 10 pour cent sur les gâteaux d'anniversaire samedi et dimanche. C'est le 01 61 23 45 67.",
  s(business_type="pâtisserie", product="gâteaux d'anniversaire", promotion="10 pour cent", location="Abomey-Calavi", phone="01 61 23 45 67", start_date="samedi", end_date="dimanche"), True, "pourcentage écrit en lettres"),
 ("restock", "Nouvel arrivage de téléphones dans ma boutique à Cadjèhoun, Cotonou. Mon numéro 0196112233.",
  s(business_type="boutique de téléphones", product="téléphones", location="Cadjèhoun, Cotonou", phone="0196112233"), True, "restock sans promo : OK, la promo n'est pas obligatoire pour un restock"),
 ("restock", "J'ai reçu du wax à Dantokpa, 6000 F le pagne. Appelez le 0196000000.",
  s(business_type="vendeuse de tissus", product="wax", price="6000 F", location="Dantokpa", phone="0196000000"), True, ""),
 ("promotion", "Séance photo à moins 25% à Ouidah ce mois-ci. Contact : 0197888999.",
  s(business_type="photographe", product="séance photo", promotion="25%", location="Ouidah", phone="0197888999"), True, "pas de jour précis"),
 ("lancement", "Je lance mon jus de bissap à Abomey-Calavi, 500 F le verre. Mon numéro, 0155443322.",
  s(business_type="vendeur de jus", product="jus de bissap", price="500 F", location="Abomey-Calavi", phone="0155443322"), True, ""),
 ("ouverture", "Ma boulangerie ouvre lundi à Bohicon, le pain est à 150 F. Numéro 98 76 54 32.",
  s(business_type="boulangerie", product="pain", price="150 F", location="Bohicon", phone="98 76 54 32", start_date="lundi"), True, ""),
 ("annonce_service", "Mon cybercafé fait la photocopie à 25 F la page, à Calavi.",
  s(business_type="cybercafé", product="photocopie", price="25 F", location="Abomey-Calavi"), False, "téléphone manquant"),
 ("annonce_service", "Électricien à Cotonou, j'installe et je répare chez vous. Appelez le 0197121212.",
  s(business_type="électricien", product="installation et réparation", location="Cotonou", phone="0197121212"), True, "service sans promo"),
 ("promotion", "Coiffeur : moins 30% mercredi et jeudi. Mon numéro 0196112233.",
  s(business_type="coiffeur", product="coiffure", promotion="30%", phone="0196112233", start_date="mercredi", end_date="jeudi"), False, "lieu manquant"),
 ("promotion", "Ma boutique d'habits fait 150% de réduction, appelez le 0197000111, c'est à Cotonou.",
  s(business_type="boutique d'habits", product="habits", promotion="150%", location="Cotonou", phone="0197000111"), False, "pourcentage impossible"),
 ("annonce_service", "Quincaillerie à Sèmè-Kpodji, ciment à 5 500 F le sac. Téléphone 12345.",
  s(business_type="quincaillerie", product="ciment", price="5 500 F", location="Sèmè-Kpodji", phone="12345"), False, "numéro invalide"),
 ("promotion", "Pour la Saint-Valentin, mon fleuriste à Saint-Michel, Cotonou, fait moins 20% sur les bouquets. 0197333444.",
  s(business_type="fleuriste", product="bouquets", promotion="20%", location="Saint-Michel, Cotonou", phone="0197333444", start_date="14 février"), True, "date implicite : Saint-Valentin = 14 février (fête à date fixe). Une promo à l'occasion d'une fête reste une promotion, pas un evenement : voir guide §2"),
 ("offre_limitee", "Sacs à moins 40% samedi seulement, ma boutique est à Cotonou. 0197555666.",
  s(business_type="boutique de sacs", product="sacs", promotion="40%", location="Cotonou", phone="0197555666", start_date="samedi"), True, ""),
 ("promotion", "Mon auto-école à Calavi donne 10 000 F de réduction sur l'inscription. Appelez le 0196777888.",
  s(business_type="auto-école", product="inscription", promotion="10 000 F", location="Abomey-Calavi", phone="0196777888"), True, "réduction en francs"),
 ("promotion", "Chaussures à Lokossa, moins 50% dimanche. Mon numéro +229 97 11 22 33.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="50%", location="Lokossa", phone="+229 97 11 22 33", start_date="dimanche"), True, "+229 devant un numéro à 8 chiffres"),
 ("promotion", "Je veux une affiche pour ma boutique à Calavi. Mon numéro 0197999000.",
  s(business_type="boutique", location="Abomey-Calavi", phone="0197999000"), False, "ni produit ni promo"),
]

# Lot 2 : 30 annonces ajoutées par Zozerigué (tâche D), suivant docs/guide_annotation.md.
# Contraintes : les 7 intentions au moins 5 fois chacune sur l'ensemble,
# environ 1 annonce sur 3 incomplète ou invalide exprès, et des contextes du
# Nigeria et du Niger (naira, numéros +234 et +227), pas seulement du Bénin.
B2 = [
 # --- evenement (le lot 1 n'en avait plus après reclassement de l'annonce 16) ---
 ("evenement", "Journée portes ouvertes samedi dans mon centre de formation à Akpakpa, Cotonou. Appelez le 0197404040.",
  s(business_type="centre de formation", event_name="Journée portes ouvertes", location="Akpakpa, Cotonou", phone="0197404040", start_date="samedi"), True, "événement sans produit ni prix : son nom et sa date sont obligatoires"),
 ("evenement", "Grande braderie dimanche au marché de Kano. Mon numéro, 08123456789.",
  s(business_type="commerce de marché", event_name="Grande braderie", location="Kano", phone="08123456789", start_date="dimanche"), True, "numéro nigérian à 11 chiffres commençant par 081"),
 ("evenement", "On organise un défilé de mode le 14 mars à Ibadan. Contact : +234 802 777 8899.",
  s(business_type="atelier de couture", product="défilé de mode", event_name="Défilé de mode", location="Ibadan", phone="+234 802 777 8899", start_date="14 mars"), True, "numéro +234 avec espaces"),
 ("evenement", "Portes ouvertes à mon école de couture à Niamey, le 5 décembre. Téléphone 96 55 44 33.",
  s(business_type="école de couture", event_name="Portes ouvertes", location="Niamey", phone="96 55 44 33", start_date="5 décembre"), True, "8 chiffres + lieu nigérien : doit donner +227 et non +229"),
 ("evenement", "Il y a une fête chez moi à Maradi, venez nombreux. Mon numéro 90 11 22 33.",
  s(business_type="commerce", location="Maradi", phone="90 11 22 33"), False, "date manquante : obligatoire pour un evenement"),
 ("evenement", "Journée promotionnelle le 30 février à Porto-Novo. 0197888111.",
  s(business_type="boutique", location="Porto-Novo", phone="0197888111", start_date="30 février"), False, "date impossible : le 30 février n'existe pas"),

 # --- lancement (1 seul dans le lot 1) ---
 ("lancement", "Je lance un service de livraison à moto à Cotonou, 1 000 F la course. Mon numéro 0197010203.",
  s(business_type="service de livraison", product="livraison à moto", price="1 000 F", location="Cotonou", phone="0197010203"), True, ""),
 ("lancement", "Nouveau yaourt maison dans ma boutique à Lagos, 500 naira le pot. Appelez le +234 806 111 2233.",
  s(business_type="boutique d'alimentation", product="yaourt maison", price="500 naira", location="Lagos", phone="+234 806 111 2233"), True, "prix en naira : la devise doit être NGN"),
 ("lancement", "Je lance mes cours de soutien scolaire à Parakou, 15 mille F le mois. 0196303030.",
  s(business_type="cours de soutien", product="cours de soutien scolaire", price="15 mille F", location="Parakou", phone="0196303030"), True, "prix écrit en lettres : 15 mille F"),
 ("lancement", "Je lance une nouvelle gamme de savons à Zinder. Mon numéro 92 44 55 66.",
  s(business_type="fabrique de savons", product="savons", location="Zinder", phone="92 44 55 66"), True, "lancement sans prix : accepté"),
 ("lancement", "Je lance quelque chose de nouveau, appelez-moi au 0197121314.",
  s(business_type="commerce", phone="0197121314"), False, "ni produit ni lieu"),

 # --- ouverture (2 dans le lot 1) ---
 ("ouverture", "Ma pharmacie ouvre le 2 novembre à Kaduna. Numéro : 08091234567.",
  s(business_type="pharmacie", location="Kaduna", phone="08091234567", start_date="2 novembre"), True, ""),
 ("ouverture", "J'ouvre une deuxième boutique à Tahoua la semaine prochaine. 97 88 99 00.",
  s(business_type="boutique", location="Tahoua", phone="97 88 99 00"), True, "« la semaine prochaine » n'est pas une date exploitable : start_date reste null, et ce n'est pas bloquant pour une ouverture"),
 ("ouverture", "Mon maquis ouvre vendredi à Bohicon, le plat est à 1 500 F. Mon numéro 0155667788.",
  s(business_type="maquis", product="plat", price="1 500 F", location="Bohicon", phone="0155667788", start_date="vendredi"), True, ""),
 ("ouverture", "Mon atelier de menuiserie ouvre bientôt à Dosso. Téléphone 94 12 13 14.",
  s(business_type="atelier de menuiserie", location="Dosso", phone="94 12 13 14"), True, "8 chiffres + Dosso : doit donner +227"),

 # --- restock (2 dans le lot 1) ---
 ("restock", "Le gaz est revenu dans mon dépôt à Godomey, 4 500 F la bouteille. 0196454545.",
  s(business_type="dépôt de gaz", product="gaz", price="4 500 F", location="Godomey", phone="0196454545"), True, "« est revenu » : c'est bien un restock, pas une annonce_service"),
 ("restock", "Nouvel arrivage de riz à Maradi, 12 mille le sac. Mon numéro 96 78 78 78.",
  s(business_type="vendeur de riz", product="riz", price="12 mille", location="Maradi", phone="96 78 78 78"), True, "prix en lettres sans unité : la devise reste indéterminée"),
 ("restock", "J'ai reçu des pièces détachées à Ibadan, ₦3500 la pièce. +234 803 909 0909.",
  s(business_type="magasin de pièces détachées", product="pièces détachées", price="₦3500", location="Ibadan", phone="+234 803 909 0909"), True, "symbole naira collé au nombre"),
 ("restock", "Les cahiers sont de nouveau disponibles, 300 F l'unité. 0197676767.",
  s(business_type="librairie", product="cahiers", price="300 F", phone="0197676767"), False, "lieu manquant"),

 # --- annonce_service (3 dans le lot 1) ---
 ("annonce_service", "Je suis plombier à Niamey, j'intervien chez vous. Mon numéro 98 23 24 25.",
  s(business_type="plombier", product="intervention à domicile", location="Niamey", phone="98 23 24 25"), True, "faute de frappe dans la transcription : on garde le texte tel quel"),
 ("annonce_service", "Mon studio photo à Lagos fait les photos d'identité, 1 500 naira. +234 805 343 4343.",
  s(business_type="studio photo", product="photos d'identité", price="1 500 naira", location="Lagos", phone="+234 805 343 4343"), True, ""),
 ("annonce_service", "Je répare les téléphones à Cotonou. Mon numéro, c'est 01 97 ... attendez ... 0197828384.",
  s(business_type="réparation de téléphones", product="réparation de téléphones", location="Cotonou", phone="0197828384"), True, "hésitation à l'oral : on annote la dernière valeur énoncée (guide §4.5)"),

 # --- promotion (10 dans le lot 1) ---
 ("promotion", "Chez moi à Agadez, le pagne passe de 8 000 à 6 500 F. Mon numéro 95 19 19 19.",
  s(business_type="vendeuse de tissus", product="pagne", price="6 500 F", promotion="1 500 F", location="Agadez", phone="95 19 19 19"), True, "prix et réduction en même temps : on remplit les deux, la réduction est la baisse (guide §4.4)"),
 ("promotion", "Pour Noël, moins 30% sur les jouets dans ma boutique à Calavi. 0196929292.",
  s(business_type="boutique de jouets", product="jouets", promotion="30%", location="Abomey-Calavi", phone="0196929292", start_date="25 décembre"), True, "fête à date fixe : Noël = 25 décembre (guide §4.1)"),
 ("promotion", "Pour la Tabaski, je fais moins 20% sur les moutons à Kano. +234 807 111 2222.",
  s(business_type="vendeur de bétail", product="moutons", promotion="20%", location="Kano", phone="+234 807 111 2222"), True, "fête mobile : la Tabaski change de date, start_date reste null (guide §4.1)"),
 ("promotion", "Au lieu de 5 000 F, venez voir mes chaussures à Porto-Novo. 0197353637.",
  s(business_type="boutique de chaussures", product="chaussures", location="Porto-Novo", phone="0197353637"), False, "« au lieu de » sans nouveau prix : ni price ni promotion, on ne calcule rien (guide §4.4)"),
 ("promotion", "Prix cassés sur les ustensiles à Dantokpa, venez. 0196141516.",
  s(business_type="vendeur d'ustensiles", product="ustensiles", location="Dantokpa", phone="0196141516"), False, "« prix cassés » n'est pas une réduction chiffrée : promotion reste null"),

 # --- offre_limitee (2 dans le lot 1) ---
 ("offre_limitee", "Du 15 au 20 octobre seulement, moins 40% sur les valises à Cotonou. 0197505152.",
  s(business_type="boutique de valises", product="valises", promotion="40%", location="Cotonou", phone="0197505152", start_date="du 15 au 20 octobre"), True, "période : start_date et end_date doivent être remplis séparément"),
 ("offre_limitee", "Du 28 octobre au 3 novembre uniquement, le poulet est à ₦2500 à Lagos. +234 809 626 2626.",
  s(business_type="restaurant", product="poulet", price="₦2500", location="Lagos", phone="+234 809 626 2626", start_date="du 28 octobre au 3 novembre"), True, "période à cheval sur deux mois"),
 ("offre_limitee", "Du vendredi au dimanche seulement, moins 15% sur la coiffure à Niamey. 93 27 28 29.",
  s(business_type="salon de coiffure", product="coiffure", promotion="15%", location="Niamey", phone="93 27 28 29", start_date="du vendredi au dimanche"), True, "période en jours nommés : start_date et end_date remplis depuis la période"),
]
B += B2

# Les deux lots sont écrits par des personnes différentes : on le note pour
# pouvoir mesurer un éventuel écart d'annotation entre annotateurs.
ANNOTATEURS = ["AQ"] * 20 + ["TZ"] * len(B2)

data = [dict(id=i + 1, transcript=t,
             slots={**sl, "language": "francais", "intent": it},
             pret_attendu=ok, piege=pg,
             source="ecrit_equipe", annotateur=ANNOTATEURS[i])
        for i, (it, t, sl, ok, pg) in enumerate(B)]
json.dump(data, open("data/briefs/briefs_fr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(data), "briefs écrits")
