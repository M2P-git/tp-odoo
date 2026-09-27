-- Semaine 2 : remplacez les deux ___ puis lancez :
-- python code/interroger.py code/requete_s2.sql
SELECT c.nom AS client,
       p.libelle AS produit,
       lc.quantite
FROM commandes AS co
JOIN clients AS c ON c.client_id = co.client_id
JOIN lignes_commandes AS lc ON lc.commande_id = ___
JOIN produits AS p ON p.produit_id = lc.produit_id
WHERE co.commande_id = ___;
