# Prépare les annonces à faire traduire par un locuteur natif.
#
# Règle absolue (voir docs/guide_annotation.md et decisions.md D-008) : personne
# dans l'équipe ne parle Yorùbá ni Hausa. On n'écrit donc AUCUN texte dans ces
# langues. On prépare le texte source en français, déjà annoté, et un locuteur
# natif fournira la traduction. Aucune traduction automatique n'est proposée :
# une traduction fausse contaminerait tout le projet.
#
# Produit : data/briefs/a_traduire_yoruba.json et a_traduire_hausa.json,
# 50 annonces chacun.
import json

from kpata.brief import nouveau_brief as s

# --------------------------------------------------------------------------- #
# Contexte par langue
# --------------------------------------------------------------------------- #
# Yorùbá : Nigeria du Sud-Ouest (Lagos, Ibadan, Abeokuta, Oyo, Osogbo, Ilorin)
#          et Sud-Est du Bénin (Porto-Novo, Kétou, Sakété). Devise dominante :
#          le naira au Nigeria, le franc CFA au Bénin.
# Hausa  : Nigeria du Nord (Kano, Kaduna, Sokoto, Katsina, Zaria, Maiduguri)
#          et Niger (Niamey, Zinder, Maradi, Tahoua, Dosso, Agadez). Devise :
#          naira au Nigeria, franc CFA au Niger.

# (intent, texte source en français, slots, prêt attendu ?, piège)
YORUBA = [
 ("promotion", "J'ai une boutique de chaussures à Ibadan. Moins 20% vendredi et samedi. Mon numéro, +234 803 111 2233.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="20%", location="Ibadan", phone="+234 803 111 2233", start_date="vendredi", end_date="samedi"), True, "cas de référence du cahier des charges, transposé au Nigeria"),
 ("promotion", "Moins 30% sur les tissus aseoke à Lagos cette semaine. 08123456001.",
  s(business_type="vendeuse de tissus", product="tissus aseoke", promotion="30%", location="Lagos", phone="08123456001"), True, "produit culturellement local"),
 ("promotion", "Les sacs passent de 12 000 à 9 000 naira à Abeokuta. +234 805 222 3344.",
  s(business_type="boutique de sacs", product="sacs", price="9 000 naira", promotion="3 000 naira", location="Abeokuta", phone="+234 805 222 3344"), True, "prix et réduction en même temps"),
 ("promotion", "Moins 15% sur le poisson fumé au marché d'Oyo. Mon numéro 08123456002.",
  s(business_type="vendeuse de poisson", product="poisson fumé", promotion="15%", location="Oyo", phone="08123456002"), True, ""),
 ("promotion", "Réduction de 25% sur les perruques à Osogbo, ce week-end. +234 807 333 4455.",
  s(business_type="salon de beauté", product="perruques", promotion="25%", location="Osogbo", phone="+234 807 333 4455", start_date="week-end"), True, "« ce week-end » : valeur relative, gardée telle quelle"),
 ("promotion", "Moins 10% sur le gari à Porto-Novo. Appelez le 0197111001.",
  s(business_type="vendeuse de vivres", product="gari", promotion="10%", location="Porto-Novo", phone="0197111001"), True, "zone yorùbá du Bénin : franc CFA"),
 ("promotion", "Moins 20% sur les pagnes à Kétou. Mon numéro 0196111002.",
  s(business_type="vendeuse de tissus", product="pagnes", promotion="20%", location="Kétou", phone="0196111002"), True, ""),
 ("promotion", "Je fais 150% de réduction sur les chaussures à Lagos. 08123456003.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="150%", location="Lagos", phone="08123456003"), False, "pourcentage impossible"),
 ("promotion", "Moins 20% sur les sacs à Ibadan. Mon numéro 12345.",
  s(business_type="boutique de sacs", product="sacs", promotion="20%", location="Ibadan", phone="12345"), False, "numéro invalide"),
 ("promotion", "Prix cassés sur les ignames à Ilorin, venez vite. 08123456004.",
  s(business_type="vendeur d'ignames", product="ignames", location="Ilorin", phone="08123456004"), False, "« prix cassés » n'est pas chiffré : promotion reste null"),
 ("promotion", "Moins 25% sur les chaussures ce samedi. +234 809 444 5566.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="25%", phone="+234 809 444 5566", start_date="samedi"), False, "lieu manquant"),
 ("promotion", "Grande réduction dans ma boutique à Lagos. 08123456005.",
  s(business_type="boutique", location="Lagos", phone="08123456005"), False, "ni produit ni réduction chiffrée"),

 ("offre_limitee", "Du 15 au 20 octobre seulement, moins 40% sur les valises à Lagos. +234 802 555 6677.",
  s(business_type="boutique de valises", product="valises", promotion="40%", location="Lagos", phone="+234 802 555 6677", start_date="du 15 au 20 octobre"), True, "période à extraire : début et fin"),
 ("offre_limitee", "Samedi uniquement, le riz jollof est à ₦2000 à Ibadan. 08123456006.",
  s(business_type="restaurant", product="riz jollof", price="₦2000", location="Ibadan", phone="08123456006", start_date="samedi"), True, "symbole naira collé au nombre ; « samedi uniquement » borne l'offre"),
 ("offre_limitee", "Du vendredi au dimanche seulement, moins 15% sur la couture à Abeokuta. +234 806 666 7788.",
  s(business_type="atelier de couture", product="couture", promotion="15%", location="Abeokuta", phone="+234 806 666 7788", start_date="du vendredi au dimanche"), True, "période en jours nommés"),
 ("offre_limitee", "Trois jours seulement, moins 20% sur les meubles à Lagos. 08123456007.",
  s(business_type="magasin de meubles", product="meubles", promotion="20%", location="Lagos", phone="08123456007"), False, "« trois jours » sans date de départ : aucune date exploitable"),
 ("offre_limitee", "Offre limitée sur les téléphones à Oyo. +234 803 777 8899.",
  s(business_type="boutique de téléphones", product="téléphones", location="Oyo", phone="+234 803 777 8899"), False, "ni prix ni réduction ni date"),

 ("lancement", "Je lance mon jus de bissap à Lagos, 300 naira le verre. 08123456008.",
  s(business_type="vendeur de jus", product="jus de bissap", price="300 naira", location="Lagos", phone="08123456008"), True, ""),
 ("lancement", "Nouveau service de livraison à moto à Ibadan, 500 naira la course. +234 805 888 9900.",
  s(business_type="service de livraison", product="livraison à moto", price="500 naira", location="Ibadan", phone="+234 805 888 9900"), True, ""),
 ("lancement", "Je lance mes cours d'informatique à Porto-Novo, 10 mille F le mois. 0197111003.",
  s(business_type="centre de formation", product="cours d'informatique", price="10 mille F", location="Porto-Novo", phone="0197111003"), True, "prix écrit en lettres"),
 ("lancement", "Je lance une nouvelle gamme de savons à Abeokuta. 08123456009.",
  s(business_type="fabrique de savons", product="savons", location="Abeokuta", phone="08123456009"), True, "lancement sans prix : accepté"),
 ("lancement", "Je lance un nouveau produit, appelez-moi. +234 807 999 0011.",
  s(business_type="commerce", phone="+234 807 999 0011"), False, "ni produit précis ni lieu"),

 ("ouverture", "Mon salon de coiffure ouvre samedi à Lagos. Les tresses sont à 3 500 naira. 08123456010.",
  s(business_type="salon de coiffure", product="tresses", price="3 500 naira", location="Lagos", phone="08123456010", start_date="samedi"), True, ""),
 ("ouverture", "Ma pharmacie ouvre le 2 novembre à Ibadan. +234 802 101 1122.",
  s(business_type="pharmacie", location="Ibadan", phone="+234 802 101 1122", start_date="2 novembre"), True, ""),
 ("ouverture", "J'ouvre une boutique de téléphones à Kétou lundi. 0196111004.",
  s(business_type="boutique de téléphones", product="téléphones", location="Kétou", phone="0196111004", start_date="lundi"), True, ""),
 ("ouverture", "Mon restaurant ouvre bientôt à Osogbo. 08123456011.",
  s(business_type="restaurant", location="Osogbo", phone="08123456011"), True, "« bientôt » n'est pas une date : non bloquant pour une ouverture"),
 ("ouverture", "J'ouvre ma boutique la semaine prochaine, venez. 08123456012.",
  s(business_type="boutique", phone="08123456012"), False, "lieu manquant"),

 ("evenement", "Journée portes ouvertes samedi dans mon centre de formation à Lagos. +234 803 121 1314.",
  s(business_type="centre de formation", location="Lagos", phone="+234 803 121 1314", start_date="samedi"), True, "evenement sans produit ni prix : accepté"),
 ("evenement", "Grande braderie dimanche au marché d'Ibadan. 08123456013.",
  s(business_type="commerce de marché", location="Ibadan", phone="08123456013", start_date="dimanche"), True, ""),
 ("evenement", "Défilé de mode le 14 mars à Abeokuta. +234 805 141 5161.",
  s(business_type="atelier de couture", product="défilé de mode", location="Abeokuta", phone="+234 805 141 5161", start_date="14 mars"), True, ""),
 ("evenement", "Fête de fin d'année dans mon école à Porto-Novo, le 20 décembre. 0197111005.",
  s(business_type="école", location="Porto-Novo", phone="0197111005", start_date="20 décembre"), True, ""),
 ("evenement", "On organise une fête chez moi à Lagos, venez nombreux. 08123456014.",
  s(business_type="commerce", location="Lagos", phone="08123456014"), False, "date manquante : obligatoire pour un evenement"),
 ("evenement", "Journée spéciale le 30 février à Ibadan. +234 807 161 7181.",
  s(business_type="boutique", location="Ibadan", phone="+234 807 161 7181", start_date="30 février"), False, "date impossible"),

 ("restock", "Nouvel arrivage de téléphones dans ma boutique à Lagos. 08123456015.",
  s(business_type="boutique de téléphones", product="téléphones", location="Lagos", phone="08123456015"), True, "restock sans promo : accepté"),
 ("restock", "J'ai reçu du tissu aseoke à Ibadan, ₦8000 le mètre. +234 802 181 9202.",
  s(business_type="vendeuse de tissus", product="tissu aseoke", price="₦8000", location="Ibadan", phone="+234 802 181 9202"), True, ""),
 ("restock", "Le gaz est revenu dans mon dépôt à Abeokuta, 4 500 naira la bouteille. 08123456016.",
  s(business_type="dépôt de gaz", product="gaz", price="4 500 naira", location="Abeokuta", phone="08123456016"), True, "« est revenu » : restock et non annonce_service"),
 ("restock", "Nouvel arrivage de riz à Porto-Novo, 20 mille F le sac. 0196111006.",
  s(business_type="vendeur de riz", product="riz", price="20 mille F", location="Porto-Novo", phone="0196111006"), True, ""),
 ("restock", "Les cahiers sont de nouveau disponibles, 500 naira. 08123456017.",
  s(business_type="librairie", product="cahiers", price="500 naira", phone="08123456017"), False, "lieu manquant"),
 ("restock", "J'ai reçu de la marchandise à Oyo. 08123456018.",
  s(business_type="boutique", location="Oyo", phone="08123456018"), False, "produit non précisé"),

 ("annonce_service", "Je suis électricien à Lagos, j'installe et je répare. +234 805 202 1222.",
  s(business_type="électricien", product="installation et réparation", location="Lagos", phone="+234 805 202 1222"), True, ""),
 ("annonce_service", "Mon studio photo à Ibadan fait les photos d'identité, 1 500 naira. 08123456019.",
  s(business_type="studio photo", product="photos d'identité", price="1 500 naira", location="Ibadan", phone="08123456019"), True, ""),
 ("annonce_service", "Je répare les téléphones à Abeokuta. +234 807 222 3242.",
  s(business_type="réparation de téléphones", product="réparation de téléphones", location="Abeokuta", phone="+234 807 222 3242"), True, ""),
 ("annonce_service", "Mon cybercafé fait la photocopie à 50 naira la page, à Osogbo. 08123456020.",
  s(business_type="cybercafé", product="photocopie", price="50 naira", location="Osogbo", phone="08123456020"), True, ""),
 ("annonce_service", "Je fais la couture sur mesure à Kétou. 0197111007.",
  s(business_type="atelier de couture", product="couture sur mesure", location="Kétou", phone="0197111007"), True, "service sans prix : accepté"),
 ("annonce_service", "Je suis plombier à Ilorin, j'intervien chez vous. 08123456021.",
  s(business_type="plombier", product="intervention à domicile", location="Ilorin", phone="08123456021"), True, "faute de frappe dans la transcription : gardée telle quelle"),
 ("annonce_service", "Quincaillerie à Lagos, ciment à ₦5500 le sac. Téléphone 999.",
  s(business_type="quincaillerie", product="ciment", price="₦5500", location="Lagos", phone="999"), False, "numéro invalide"),
 ("annonce_service", "Je propose mes services, appelez-moi au 08123456022.",
  s(business_type="commerce", phone="08123456022"), False, "ni service précis ni lieu"),

 # --- compléments pour atteindre 50 ---
 ("promotion", "Moins 35% sur les bijoux à Lagos, du 1er au 5 mars. +234 803 232 4252.",
  s(business_type="bijouterie", product="bijoux", promotion="35%", location="Lagos", phone="+234 803 232 4252", start_date="du 1er au 5 mars"), True, "période avec « 1er » : le début doit rester le 1 mars"),
 ("restock", "Le ciment est revenu à Ilorin, ₦5200 le sac. 08123456023.",
  s(business_type="quincaillerie", product="ciment", price="₦5200", location="Ilorin", phone="08123456023"), True, ""),
 ("ouverture", "Mon maquis ouvre le 1er novembre à Sakété, le plat est à 1 500 F. 0196111008.",
  s(business_type="maquis", product="plat", price="1 500 F", location="Sakété", phone="0196111008", start_date="1er novembre"), True, "« 1er novembre » : le code doit lire le jour 1"),
]

HAUSA = [
 ("promotion", "J'ai une boutique de chaussures à Kano. Moins 20% vendredi et samedi. +234 803 301 1223.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="20%", location="Kano", phone="+234 803 301 1223", start_date="vendredi", end_date="samedi"), True, "cas de référence du cahier des charges, transposé au Nord"),
 ("promotion", "Moins 25% sur les sacs de ciment à Kano cette semaine. 08133456001.",
  s(business_type="quincaillerie", product="sacs de ciment", promotion="25%", location="Kano", phone="08133456001"), True, ""),
 ("promotion", "Le pagne passe de 8 000 à 6 500 F chez moi à Maradi. 96 30 10 01.",
  s(business_type="vendeuse de tissus", product="pagne", price="6 500 F", promotion="1 500 F", location="Maradi", phone="96 30 10 01"), True, "8 chiffres + ville nigérienne : doit donner +227"),
 ("promotion", "Moins 15% sur le mil au marché de Zinder. 92 30 10 02.",
  s(business_type="vendeur de céréales", product="mil", promotion="15%", location="Zinder", phone="92 30 10 02"), True, "produit local du Sahel"),
 ("promotion", "Réduction de 30% sur les babouches à Sokoto. +234 805 302 2334.",
  s(business_type="vendeur de chaussures", product="babouches", promotion="30%", location="Sokoto", phone="+234 805 302 2334"), True, ""),
 ("promotion", "Pour la Tabaski, moins 20% sur les moutons à Kano. 08133456002.",
  s(business_type="vendeur de bétail", product="moutons", promotion="20%", location="Kano", phone="08133456002"), True, "fête mobile : la Tabaski change de date, start_date reste null"),
 ("promotion", "Moins 10% sur le lait caillé à Niamey. 97 30 10 03.",
  s(business_type="vendeuse de lait", product="lait caillé", promotion="10%", location="Niamey", phone="97 30 10 03"), True, ""),
 ("promotion", "Je fais 200% de réduction sur les tissus à Kaduna. +234 807 303 3445.",
  s(business_type="vendeur de tissus", product="tissus", promotion="200%", location="Kaduna", phone="+234 807 303 3445"), False, "pourcentage impossible"),
 ("promotion", "Moins 20% sur les sacs à Katsina. Mon numéro 55.",
  s(business_type="boutique de sacs", product="sacs", promotion="20%", location="Katsina", phone="55"), False, "numéro invalide"),
 ("promotion", "Prix cassés sur le riz à Tahoua, venez vite. 93 30 10 04.",
  s(business_type="vendeur de riz", product="riz", location="Tahoua", phone="93 30 10 04"), False, "« prix cassés » n'est pas chiffré"),
 ("promotion", "Moins 25% sur les chaussures samedi. 08133456003.",
  s(business_type="boutique de chaussures", product="chaussures", promotion="25%", phone="08133456003", start_date="samedi"), False, "lieu manquant"),
 ("promotion", "Grande promotion dans ma boutique à Kano. +234 802 304 4556.",
  s(business_type="boutique", location="Kano", phone="+234 802 304 4556"), False, "ni produit ni réduction chiffrée"),

 ("offre_limitee", "Du 15 au 20 octobre seulement, moins 40% sur les valises à Kaduna. 08133456004.",
  s(business_type="boutique de valises", product="valises", promotion="40%", location="Kaduna", phone="08133456004", start_date="du 15 au 20 octobre"), True, "période à extraire"),
 ("offre_limitee", "Du 28 octobre au 3 novembre uniquement, la viande grillée est à ₦1500 à Kano. +234 805 305 5667.",
  s(business_type="grillade", product="viande grillée", price="₦1500", location="Kano", phone="+234 805 305 5667", start_date="du 28 octobre au 3 novembre"), True, "période à cheval sur deux mois"),
 ("offre_limitee", "Du vendredi au dimanche seulement, moins 15% sur la coiffure à Niamey. 91 30 10 05.",
  s(business_type="salon de coiffure", product="coiffure", promotion="15%", location="Niamey", phone="91 30 10 05", start_date="du vendredi au dimanche"), True, "période en jours nommés"),
 ("offre_limitee", "Deux jours seulement, moins 20% sur les meubles à Zinder. 94 30 10 06.",
  s(business_type="magasin de meubles", product="meubles", promotion="20%", location="Zinder", phone="94 30 10 06"), False, "« deux jours » sans date de départ"),
 ("offre_limitee", "Offre limitée sur les téléphones à Sokoto. 08133456005.",
  s(business_type="boutique de téléphones", product="téléphones", location="Sokoto", phone="08133456005"), False, "ni prix ni réduction ni date"),

 ("lancement", "Je lance mon jus de tamarin à Niamey, 200 F le sachet. 98 30 10 07.",
  s(business_type="vendeur de jus", product="jus de tamarin", price="200 F", location="Niamey", phone="98 30 10 07"), True, ""),
 ("lancement", "Nouveau service de livraison à Kano, 500 naira la course. +234 807 306 6778.",
  s(business_type="service de livraison", product="livraison", price="500 naira", location="Kano", phone="+234 807 306 6778"), True, ""),
 ("lancement", "Je lance mes cours de couture à Maradi, 8 mille F le mois. 90 30 10 08.",
  s(business_type="atelier de couture", product="cours de couture", price="8 mille F", location="Maradi", phone="90 30 10 08"), True, "prix écrit en lettres"),
 ("lancement", "Je lance une nouvelle gamme de parfums à Kaduna. 08133456006.",
  s(business_type="boutique de parfums", product="parfums", location="Kaduna", phone="08133456006"), True, "lancement sans prix : accepté"),
 ("lancement", "Je lance un nouveau produit, appelez-moi. 95 30 10 09.",
  s(business_type="commerce", phone="95 30 10 09"), False, "ni produit précis ni lieu"),

 ("ouverture", "Mon salon de coiffure ouvre samedi à Kano. Les tresses sont à 3 500 naira. +234 802 307 7889.",
  s(business_type="salon de coiffure", product="tresses", price="3 500 naira", location="Kano", phone="+234 802 307 7889", start_date="samedi"), True, ""),
 ("ouverture", "Ma pharmacie ouvre le 2 novembre à Zinder. 96 30 10 10.",
  s(business_type="pharmacie", location="Zinder", phone="96 30 10 10", start_date="2 novembre"), True, ""),
 ("ouverture", "J'ouvre une boutique de téléphones à Katsina lundi. 08133456007.",
  s(business_type="boutique de téléphones", product="téléphones", location="Katsina", phone="08133456007", start_date="lundi"), True, ""),
 ("ouverture", "Mon atelier de menuiserie ouvre bientôt à Dosso. 94 30 10 11.",
  s(business_type="atelier de menuiserie", location="Dosso", phone="94 30 10 11"), True, "« bientôt » n'est pas une date : non bloquant"),
 ("ouverture", "J'ouvre mon commerce la semaine prochaine, venez. 08133456008.",
  s(business_type="commerce", phone="08133456008"), False, "lieu manquant"),

 ("evenement", "Journée portes ouvertes samedi dans mon centre de formation à Kano. +234 805 308 8990.",
  s(business_type="centre de formation", location="Kano", phone="+234 805 308 8990", start_date="samedi"), True, "evenement sans produit ni prix : accepté"),
 ("evenement", "Grande braderie dimanche au marché de Maradi. 92 30 10 12.",
  s(business_type="commerce de marché", location="Maradi", phone="92 30 10 12", start_date="dimanche"), True, ""),
 ("evenement", "Course de chevaux le 14 mars à Katsina. 08133456009.",
  s(business_type="organisateur d'événements", product="course de chevaux", location="Katsina", phone="08133456009", start_date="14 mars"), True, "événement culturel du Nord"),
 ("evenement", "Fête de fin d'année dans mon école à Niamey, le 20 décembre. 97 30 10 13.",
  s(business_type="école", location="Niamey", phone="97 30 10 13", start_date="20 décembre"), True, ""),
 ("evenement", "On organise une fête chez moi à Tahoua, venez nombreux. 93 30 10 14.",
  s(business_type="commerce", location="Tahoua", phone="93 30 10 14"), False, "date manquante"),
 ("evenement", "Journée spéciale le 32 mars à Kano. 08133456010.",
  s(business_type="boutique", location="Kano", phone="08133456010", start_date="32 mars"), False, "date impossible"),

 ("restock", "Nouvel arrivage de téléphones dans ma boutique à Kano. +234 807 309 9001.",
  s(business_type="boutique de téléphones", product="téléphones", location="Kano", phone="+234 807 309 9001"), True, "restock sans promo : accepté"),
 ("restock", "J'ai reçu du mil à Zinder, 12 mille le sac. 91 30 10 15.",
  s(business_type="vendeur de céréales", product="mil", price="12 mille", location="Zinder", phone="91 30 10 15"), True, "prix en lettres sans unité : devise indéterminée"),
 ("restock", "Le gaz est revenu dans mon dépôt à Kaduna, ₦4500 la bouteille. 08133456011.",
  s(business_type="dépôt de gaz", product="gaz", price="₦4500", location="Kaduna", phone="08133456011"), True, "« est revenu » : restock"),
 ("restock", "Nouvel arrivage d'engrais à Dosso, 15 000 F le sac. 90 30 10 16.",
  s(business_type="vendeur d'intrants", product="engrais", price="15 000 F", location="Dosso", phone="90 30 10 16"), True, ""),
 ("restock", "Les cahiers sont de nouveau disponibles, 500 naira. 08133456012.",
  s(business_type="librairie", product="cahiers", price="500 naira", phone="08133456012"), False, "lieu manquant"),
 ("restock", "J'ai reçu de la marchandise à Sokoto. +234 802 310 1123.",
  s(business_type="boutique", location="Sokoto", phone="+234 802 310 1123"), False, "produit non précisé"),

 ("annonce_service", "Je suis électricien à Kano, j'installe et je répare. 08133456013.",
  s(business_type="électricien", product="installation et réparation", location="Kano", phone="08133456013"), True, ""),
 ("annonce_service", "Mon studio photo à Kaduna fait les photos d'identité, 1 500 naira. +234 805 311 2234.",
  s(business_type="studio photo", product="photos d'identité", price="1 500 naira", location="Kaduna", phone="+234 805 311 2234"), True, ""),
 ("annonce_service", "Je fais le transfert d'argent et le retrait à Zinder. 95 30 10 17.",
  s(business_type="point de transfert d'argent", product="transfert d'argent et retrait", location="Zinder", phone="95 30 10 17"), True, ""),
 ("annonce_service", "Mon cybercafé fait la photocopie à 25 F la page, à Niamey. 98 30 10 18.",
  s(business_type="cybercafé", product="photocopie", price="25 F", location="Niamey", phone="98 30 10 18"), True, ""),
 ("annonce_service", "Je répare les motos à Maradi. 96 30 10 19.",
  s(business_type="mécanicien", product="réparation de motos", location="Maradi", phone="96 30 10 19"), True, "service sans prix : accepté"),
 ("annonce_service", "Je suis plombier à Katsina, j'intervien chez vous. 08133456014.",
  s(business_type="plombier", product="intervention à domicile", location="Katsina", phone="08133456014"), True, "faute de frappe gardée telle quelle"),
 ("annonce_service", "Quincaillerie à Sokoto, ciment à ₦5500 le sac. Téléphone 777.",
  s(business_type="quincaillerie", product="ciment", price="₦5500", location="Sokoto", phone="777"), False, "numéro invalide"),
 ("annonce_service", "Je propose mes services, appelez-moi au 94 30 10 20.",
  s(business_type="commerce", phone="94 30 10 20"), False, "ni service précis ni lieu"),

 # --- compléments pour atteindre 50 ---
 ("promotion", "Moins 35% sur les bijoux à Kano, du 1er au 5 mars. +234 807 312 3345.",
  s(business_type="bijouterie", product="bijoux", promotion="35%", location="Kano", phone="+234 807 312 3345", start_date="du 1er au 5 mars"), True, "période avec « 1er » : le début doit rester le 1 mars"),
 ("restock", "Le ciment est revenu à Tahoua, 6 000 F le sac. 92 30 10 21.",
  s(business_type="quincaillerie", product="ciment", price="6 000 F", location="Tahoua", phone="92 30 10 21"), True, ""),
 ("ouverture", "Mon restaurant ouvre le 1er novembre à Agadez, le plat est à 1 200 F. 97 30 10 22.",
  s(business_type="restaurant", product="plat", price="1 200 F", location="Agadez", phone="97 30 10 22", start_date="1er novembre"), True, "« 1er novembre » : le code doit lire le jour 1"),
]


def construire(annonces, langue):
    """Une annonce à traduire : le texte source en français, les slots annotés,
    et un champ de traduction laissé VIDE pour le locuteur natif."""
    return [
        {
            "id": i + 1,
            "langue_cible": langue,
            "transcript_source_fr": texte,
            "transcript": None,          # à remplir par le locuteur natif
            "slots": {**slots, "language": langue, "intent": intent},
            "pret_attendu": pret,
            "piege": piege,
            "source": "a_traduire",
            "annotateur": "TZ",
            "traducteur": None,          # initiales du locuteur, à remplir
        }
        for i, (intent, texte, slots, pret, piege) in enumerate(annonces)
    ]


if __name__ == "__main__":
    for langue, annonces in [("yoruba", YORUBA), ("hausa", HAUSA)]:
        chemin = f"data/briefs/a_traduire_{langue}.json"
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(construire(annonces, langue), f, ensure_ascii=False, indent=2)
        print(len(annonces), "annonces à traduire ->", chemin)
