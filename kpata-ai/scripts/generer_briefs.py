# Génère briefs_fr.json : les annonces annotées en français
# Format et règles d'annotation : docs/guide_annotation.md
import json

from kpata.brief import nouveau_brief as s

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

data = [dict(id=i + 1, transcript=t, slots={**sl, "language": "francais", "intent": it},
             pret_attendu=ok, piege=pg) for i, (it, t, sl, ok, pg) in enumerate(B)]
json.dump(data, open("data/briefs/briefs_fr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(data), "briefs écrits")
