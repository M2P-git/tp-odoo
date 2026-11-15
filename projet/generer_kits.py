# Génère les kits de produits de la séance 7 (un fichier CSV par type de boutique).
#   python generer_kits.py   -> projet/kits/kit-*.csv
# Même en-tête que modele-produits.csv : les colonnes sont reconnues automatiquement par l'import d'Odoo.
# Prix de vente et coûts hors taxes, en dirhams. Produits génériques : chaque étudiant renomme sa boutique et ses articles s'il le souhaite.
import os

ENTETE = "Nom;Référence interne;Prix de vente;Coût;Type de produit;Catégories du site web;Description eCommerce;Est publié"

KITS = {
"kit-vetements": [
("T-shirt basique coton bio", "VET-01", 149, 55, "Vêtements", "Coton bio 180 g, coupe droite."),
("Sweat à capuche", "VET-02", 399, 160, "Vêtements", "Molleton épais, poche kangourou."),
("Pantalon cargo", "VET-03", 349, 140, "Vêtements", "Toile résistante, six poches."),
("Veste en jean", "VET-04", 499, 210, "Vêtements", "Denim brut, boutons métalliques."),
("Chemise en lin", "VET-05", 299, 115, "Vêtements", "Lin léger, idéale pour l'été."),
("Casquette brodée", "VET-06", 129, 45, "Accessoires", "Coton sergé, logo brodé."),
("Bonnet en maille", "VET-07", 99, 35, "Accessoires", "Maille côtelée, taille unique."),
("Tote bag imprimé", "VET-08", 89, 28, "Accessoires", "Toile de coton 280 g."),
("Chaussettes, lot de 3", "VET-09", 79, 25, "Accessoires", "Coton peigné, taille 39-45."),
("Ceinture en cuir", "VET-10", 189, 70, "Accessoires", "Cuir pleine fleur, boucle argentée."),
("Sac banane", "VET-11", 159, 60, "Accessoires", "Nylon déperlant, sangle réglable."),
("Carte cadeau 200 DH", "VET-12", 200, 0, "Cartes cadeaux", "À offrir, valable un an."),
],
"kit-cafe-the": [
("Café en grains Éthiopie 250 g", "CAF-01", 120, 55, "Cafés", "Notes florales et d'agrumes."),
("Café en grains Colombie 250 g", "CAF-02", 105, 48, "Cafés", "Chocolat au lait, noisette."),
("Café en grains Brésil 250 g", "CAF-03", 95, 42, "Cafés", "Doux, peu acide."),
("Mélange maison 1 kg", "CAF-04", 290, 130, "Cafés", "Pour espresso et cafetière italienne."),
("Thé vert à la menthe 100 g", "CAF-05", 45, 18, "Thés", "Gunpowder et menthe nanah séchée."),
("Infusion verveine 50 g", "CAF-06", 35, 12, "Thés", "Verveine de l'Atlas."),
("Théière en métal argenté", "CAF-07", 260, 120, "Accessoires", "Théière traditionnelle, 1 litre."),
("Verres à thé, coffret de 6", "CAF-08", 120, 50, "Accessoires", "Verres décorés, 15 cl."),
("Moulin à café manuel", "CAF-09", 350, 170, "Accessoires", "Meules en céramique, mouture réglable."),
("Mug en céramique", "CAF-10", 85, 35, "Accessoires", "35 cl, passe au lave-vaisselle."),
("Coffret découverte trois cafés", "CAF-11", 280, 120, "Coffrets", "Trois sachets de 100 g."),
("Atelier dégustation (une personne)", "CAF-12", 150, 0, "Ateliers", "Deux heures, le samedi matin.", "Service"),
],
"kit-cosmetiques": [
("Huile d'argan cosmétique 100 ml", "COS-01", 140, 65, "Visage", "Pure, pressée à froid."),
("Savon noir à l'eucalyptus 250 g", "COS-02", 45, 15, "Hammam", "Pour le gommage au gant kessa."),
("Gant kessa", "COS-03", 30, 10, "Hammam", "Gant exfoliant traditionnel."),
("Ghassoul en poudre 200 g", "COS-04", 40, 14, "Hammam", "Argile lavante de l'Atlas."),
("Eau de rose 200 ml", "COS-05", 55, 20, "Visage", "Lotion tonique de la vallée du Dadès."),
("Crème hydratante à l'argan 50 ml", "COS-06", 120, 48, "Visage", "Texture légère, tous types de peau."),
("Beurre de karité 100 g", "COS-07", 70, 28, "Corps", "Pur, non raffiné."),
("Huile de nigelle 100 ml", "COS-08", 90, 38, "Corps", "Pour les cheveux et la peau."),
("Shampoing solide au ghassoul", "COS-09", 65, 22, "Cheveux", "Sans sulfate, 80 g."),
("Bougie parfumée fleur d'oranger", "COS-10", 110, 40, "Maison", "Cire végétale, 40 heures."),
("Coffret hammam", "COS-11", 220, 90, "Coffrets", "Savon noir, kessa, ghassoul, eau de rose."),
("Soin visage en institut", "COS-12", 300, 0, "Soins", "Une heure, sur rendez-vous.", "Service"),
],
"kit-high-tech": [
("Écouteurs sans fil", "TEC-01", 299, 150, "Audio", "Réduction de bruit, 24 h d'autonomie."),
("Enceinte Bluetooth portable", "TEC-02", 349, 180, "Audio", "Étanche, 12 h d'autonomie."),
("Chargeur rapide USB-C 30 W", "TEC-03", 149, 65, "Charge", "Compatible téléphones et tablettes."),
("Batterie externe 10 000 mAh", "TEC-04", 199, 95, "Charge", "Deux ports, charge rapide."),
("Câble USB-C tressé 1 m", "TEC-05", 59, 18, "Charge", "Nylon tressé, 60 W."),
("Coque de téléphone silicone", "TEC-06", 79, 22, "Protection", "Plusieurs modèles de téléphones."),
("Verre trempé", "TEC-07", 49, 12, "Protection", "Dureté 9H, pose facile."),
("Support de téléphone pour voiture", "TEC-08", 129, 50, "Accessoires", "Fixation magnétique."),
("Clé USB 64 Go", "TEC-09", 89, 38, "Stockage", "USB 3.2."),
("Souris sans fil", "TEC-10", 139, 60, "Accessoires", "Silencieuse, 18 mois d'autonomie."),
("Montre connectée", "TEC-11", 499, 260, "Objets connectés", "Suivi d'activité et notifications."),
("Installation et réglage (une heure)", "TEC-12", 150, 0, "Services", "À domicile, à Rabat.", "Service"),
],
"kit-patisserie-epicerie": [
("Cornes de gazelle (500 g)", "PAT-01", 140, 60, "Pâtisseries", "Pâte fine, amandes et fleur d'oranger."),
("Ghriba aux amandes (500 g)", "PAT-02", 90, 38, "Pâtisseries", "Moelleuse et craquelée."),
("Chebakia au miel (500 g)", "PAT-03", 75, 30, "Pâtisseries", "Sésame, miel, eau de fleur d'oranger."),
("Fekkas aux amandes (500 g)", "PAT-04", 70, 28, "Pâtisseries", "Biscuit croquant."),
("Coffret assortiment 24 pièces", "PAT-05", 220, 95, "Coffrets", "Pour les fêtes et les invités."),
("Amlou 250 g", "PAT-06", 90, 42, "Épicerie fine", "Amandes, huile d'argan, miel."),
("Miel de thym 500 g", "PAT-07", 150, 90, "Épicerie fine", "Récolte de l'Atlas."),
("Huile d'olive extra vierge 1 L", "PAT-08", 120, 75, "Épicerie fine", "Première pression à froid."),
("Dattes Medjool 1 kg", "PAT-09", 160, 95, "Épicerie fine", "Calibre extra."),
("Confiture de figues 300 g", "PAT-10", 55, 20, "Épicerie fine", "Préparation artisanale."),
("Ras el hanout 100 g", "PAT-11", 40, 15, "Épices", "Mélange de 25 épices."),
("Commande pour un événement (acompte)", "PAT-12", 500, 0, "Événements", "Acompte pour une commande sur mesure.", "Service"),
],
"kit-sport-nutrition": [
("Protéine whey 1 kg", "SPO-01", 420, 260, "Nutrition", "Saveur chocolat, 33 doses."),
("Barre protéinée", "SPO-02", 18, 9, "Nutrition", "20 g de protéines."),
("Créatine 300 g", "SPO-03", 250, 140, "Nutrition", "Monohydrate pure."),
("Boisson isotonique 500 ml", "SPO-04", 15, 6, "Nutrition", "Saveur citron."),
("Shaker 600 ml", "SPO-05", 60, 22, "Accessoires", "Sans BPA, avec grille."),
("Tapis de yoga", "SPO-06", 199, 85, "Équipement", "6 mm, antidérapant."),
("Paire d'haltères 2 × 5 kg", "SPO-07", 350, 190, "Équipement", "Revêtement néoprène."),
("Corde à sauter", "SPO-08", 69, 25, "Équipement", "Câble réglable, roulements."),
("Gourde isotherme 750 ml", "SPO-09", 149, 60, "Accessoires", "Garde le froid 24 h."),
("T-shirt de sport respirant", "SPO-10", 159, 60, "Textile", "Séchage rapide."),
("Séance de coaching individuel", "SPO-11", 250, 0, "Coaching", "45 minutes avec un coach.", "Service"),
("Abonnement mensuel salle", "SPO-12", 350, 0, "Abonnements", "Accès illimité pendant un mois.", "Service"),
],
}

ici = os.path.dirname(os.path.abspath(__file__))
dossier = os.path.join(ici, "kits")
os.makedirs(dossier, exist_ok=True)
for nom, lignes in KITS.items():
    sortie = [ENTETE]
    for l in lignes:
        type_ = l[6] if len(l) > 6 else "Biens"
        sortie.append(";".join([l[0], l[1], str(l[2]), str(l[3]), type_, l[4], l[5], "1"]))
    with open(os.path.join(dossier, nom + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sortie) + "\n")
    print(nom, len(lignes), "produits")
