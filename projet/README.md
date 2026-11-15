# Séance 7 et projet de fin de module : votre boutique dans Odoo

Fichiers à télécharger en début de séance 7, pour importer le catalogue de votre boutique dans votre base Odoo Online.

## Choisir un kit

Chaque kit contient douze produits prêts à importer : nom, référence, prix de vente et coût hors taxes, catégorie de la boutique, description. Choisissez le kit le plus proche de la boutique que vous voulez créer ; vous pourrez renommer les produits et modifier les prix après l'import.

| Fichier | Type de boutique | Produit à décliner en variantes (à faire à la main) |
|---|---|---|
| `kits/kit-vetements.csv` | Mode urbaine | T-shirt basique : tailles S, M, L, XL |
| `kits/kit-cafe-the.csv` | Café et thé | Café en grains : mouture (grains, espresso, filtre) |
| `kits/kit-cosmetiques.csv` | Cosmétiques naturels | Huile d'argan : contenance (50 ml, 100 ml) |
| `kits/kit-high-tech.csv` | Accessoires high-tech | Coque de téléphone : modèle de téléphone |
| `kits/kit-patisserie-epicerie.csv` | Pâtisserie et épicerie fine | Coffret assortiment : 12 ou 24 pièces |
| `kits/kit-sport-nutrition.csv` | Sport et nutrition | Protéine whey : saveur (chocolat, vanille) |

Vous avez déjà une idée de boutique qui ne correspond à aucun kit ? Partez de `modele-produits.csv` et remplissez-le avec vos propres produits.

Les **images** ne sont pas fournies : chacun télécharge les siennes, libres de droits (par exemple sur Unsplash, Pexels ou Pixabay) ou prises par lui-même, ainsi qu'un logo pour sa boutique.

`atlas-wear-produits.csv` contient les produits de la démonstration de l'enseignant (boutique Atlas Wear).

## Remplir ou modifier un fichier

- Gardez la première ligne telle quelle : ce sont les noms des champs d'Odoo, la correspondance des colonnes se fait alors toute seule.
- Une ligne par produit. Le séparateur est le point-virgule ; l'encodage est UTF-8.
- **Prix de vente** et **Coût** : hors taxes, sans unité (`199`, pas `199 DH`).
- **Type de produit** : `Biens` ou `Service`, exactement (Odoo 20 refuse `Bien`).
- **Catégories du site web** : le nom de la catégorie de votre boutique.
- **Est publié** : `1` pour afficher le produit sur la boutique, `0` sinon.

Ouvrez le fichier avec LibreOffice Calc ou Excel (Données, À partir d'un fichier texte, encodage UTF-8, séparateur point-virgule) et enregistrez-le au format CSV.

## Importer dans Odoo

Liste des produits, menu d'actions (engrenage), **Importer**, choisir le fichier, **Tester**.

Dans une base neuve, les catégories de la boutique n'existent pas encore : Odoo affiche « Aucun enregistrement correspondant trouvé » et propose un choix sous « Lorsqu'une valeur ne peut pas être mise en correspondance ». Choisissez **Créer de nouvelles valeurs**, testez à nouveau, puis **Importer**.

Les photos ne viennent pas avec le fichier : ajoutez-les ensuite sur chaque fiche produit.

Les kits sont produits par `generer_kits.py` (`python generer_kits.py`).
