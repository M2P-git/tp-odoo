# Projet de fin de module : votre entreprise, votre Odoo

Fichiers de la séance 7, pour importer le catalogue de votre commerce dans votre base Odoo Online.

| Fichier | Rôle |
|---|---|
| `modele-produits.csv` | Modèle à compléter avec les produits de votre commerce (au moins sept). |
| `atlas-wear-produits.csv` | Exemple rempli : les sept produits importés par Atlas Wear pendant la démonstration. |

## Remplir le modèle

- Gardez la première ligne telle quelle : ce sont les noms des champs d'Odoo, la correspondance des colonnes se fait alors toute seule.
- Une ligne par produit. Le séparateur est le point-virgule ; l'encodage est UTF-8.
- **Prix de vente** et **Coût** : hors taxes, sans unité (`199`, pas `199 DH`).
- **Type de produit** : `Biens` ou `Service`, exactement (Odoo 20 refuse `Bien`).
- **Catégories du site web** : le nom de la catégorie de votre boutique ; une catégorie absente est créée à l'import.
- **Est publié** : `1` pour afficher le produit sur la boutique, `0` sinon.

Ouvrez le fichier avec LibreOffice Calc ou Excel (Données, À partir d'un fichier texte, encodage UTF-8, séparateur point-virgule) et enregistrez-le au format CSV.

## Importer dans Odoo

Liste des produits, menu d'actions (engrenage), **Importer**, choisir le fichier, **Tester**, puis **Importer**. Les photos ne viennent pas avec le fichier : ajoutez-les ensuite sur chaque fiche produit.
