# erp-crm-ci3bi : environnement de TP

Dépôt du module **« Gestion intégrée des systèmes ERP et CRM »** (Cycle d'ingénieurs en Business Intelligence, CI3 BI).
Il installe sur votre poste un **Odoo 19** déjà rempli avec les données de notre entreprise fictive **Atlas Micro**,
ainsi que les fichiers CSV et les scripts Python/SQL des exercices.

> **Une seule commande** prépare tout : Odoo, sa base PostgreSQL et le jeu Atlas Micro.
> Aucune saisie manuelle n'est nécessaire.

---

## 1. Ce qu'il vous faut

| Élément | Minimum | Conseillé |
|---|---|---|
| Système | Windows 10/11 64 bits, macOS 12+ ou Linux | Windows 11 ou macOS récent |
| Mémoire vive | 4 Go | 8 Go ou plus |
| Espace disque libre | 6 Go | 10 Go |
| Droits | Administrateur du PC pour installer Docker Desktop | - |
| Réseau | ~1 Go à télécharger la première fois (ou clé USB distribuée en classe) | - |

Sous Windows, la **virtualisation** doit être activée dans le BIOS/UEFI (c'est le cas sur la plupart des PC récents).

## 2. Installer Docker Desktop (une seule fois)

1. Téléchargez Docker Desktop : <https://www.docker.com/products/docker-desktop/>.
2. Lancez l'installateur, gardez les options par défaut (**WSL 2** sous Windows), puis **redémarrez** le PC si demandé.
3. Ouvrez Docker Desktop et attendez l'indication **« Engine running »** en bas à gauche.
4. Vérifiez dans un terminal (PowerShell sous Windows) : `docker --version` puis `docker compose version`.

## 3. Récupérer ce dépôt

**Avec Git** (conseillé), dans un dossier simple, par exemple `C:\cours` :

```bash
git clone https://github.com/VOTRE-COMPTE/erp-crm-ci3bi.git
cd erp-crm-ci3bi
```

**Sans Git** : sur la page GitHub du dépôt, bouton vert **Code → Download ZIP**, puis décompressez le fichier
(clic droit → *Extraire tout*). Évitez les dossiers synchronisés (OneDrive, Google Drive).

## 4. Démarrer Odoo

| Windows | macOS / Linux |
|---|---|
| Double-cliquez sur **`demarrer.cmd`** | `./demarrer.sh` dans un terminal |

La **première fois**, le script télécharge les images (≈ 1 Go) puis prépare la base `atlas_micro` :
comptez **5 à 15 minutes** selon le réseau et le PC. Les fois suivantes, le démarrage prend quelques secondes.
À la fin, le navigateur s'ouvre sur <http://localhost:8069>.

| Connexion | Valeur |
|---|---|
| Adresse | <http://localhost:8069> |
| Identifiant | `admin` |
| Mot de passe | `admin` |

Équivalent en ligne de commande : `docker compose up -d`.

## 5. Vérifier, arrêter, repartir de zéro

| Besoin | Windows | macOS / Linux |
|---|---|---|
| Vérifier que le jeu Atlas Micro est bien chargé | `verifier.cmd` | `./verifier.sh` |
| Arrêter en gardant les données | `arreter.cmd` | `./arreter.sh` |
| Tout effacer et recréer le jeu initial | `reinitialiser.cmd` | `./reinitialiser.sh` |

`verifier` affiche une ligne `[OK ]` par contrôle. Après un TP, des lignes `[ECART]` sont normales :
vous avez fait évoluer les données (réception validée, devis confirmé…).

## 6. Ce que contient la base Atlas Micro

| Objet | Contenu initial |
|---|---|
| Société | Atlas Micro, Rabat, devise **MAD** |
| Acteurs internes | Sara Alaoui (commerciale), Hamza Tazi (magasinier), Leïla Benjelloun (acheteuse), Youssef Amrani (comptable) |
| Clients | `C001` Nova Conseil (contact Yassine), `C002` École Sigma (Karim), `C003` MediTech (Salma) |
| Fournisseurs | `F01` TechRoute (routeur 780 MAD, 5 jours), `F02` DockPro, `F03` AltRoute (routeur 950 MAD, 2 jours) |
| Produits suivis en stock | `P-R10` Routeur Pro R10 (1 200 MAD, **6 en stock**), `P-D02` Station d'accueil D2 (450 MAD, 8 en stock) |
| Ventes | `CO104` Nova Conseil, 10 routeurs, **confirmée**, livraison en attente ; `CO105` École Sigma, 2 routeurs, **devis** ; `CO106` MediTech, 3 stations, confirmée |
| Réapprovisionnement | Règle `P-R10` : minimum 3, maximum 12, déclenchement manuel |
| CRM | Campagnes *Webinaire* et *Salon*, **10 pistes importées telles quelles** (dont 2 doublons volontaires), 2 activités planifiées |

Toutes les données sont **fictives**.

## 7. Exercices Python et SQL (sans Odoo)

Les dossiers `data/` et `code/` contiennent une petite base pédagogique **SQLite** (ce n'est pas le schéma d'Odoo).
Avec Python 3.10 ou plus, depuis le dossier du dépôt :

```bash
python code/initialiser.py                        # crée data/atlas_micro.sqlite
python code/interroger.py code/requete_s2.sql     # séance 2 : requête à compléter
python code/import_prospects_a_completer.py       # séance 3 : dédoublonnage des prospects
python code/calcul_stock_a_completer.py           # séance 4 : calcul de réapprovisionnement
```

## 8. En cas de problème

| Symptôme | Solution |
|---|---|
| `docker` n'est pas reconnu | Docker Desktop n'est pas installé ou pas lancé : ouvrez-le et attendez « Engine running ». |
| Docker Desktop demande WSL | Dans PowerShell **administrateur** : `wsl --install`, puis redémarrez. |
| « Virtualization support not detected » | Activez la virtualisation (Intel VT-x / AMD-V) dans le BIOS/UEFI. |
| Port 8069 déjà utilisé | Un autre Odoo tourne : `docker ps`, arrêtez-le, puis relancez `demarrer`. |
| Le démarrage échoue | Ouvrez `demarrage.log` et montrez-le ; puis essayez `reinitialiser`. |
| Page blanche ou erreur 500 juste après le démarrage | Attendez 30 secondes et rechargez la page. |
| PC trop lent ou sans droits administrateur | Travaillez en binôme sur le poste d'un camarade. |

## 9. Installation hors ligne (clé USB)

Pour éviter que toute la classe télécharge les mêmes images en même temps :

```bash
# sur un poste déjà prêt
docker save -o atlas-images.tar odoo:19.0 postgres:16
# sur chaque poste, depuis la clé USB
docker load -i atlas-images.tar
```

Puis lancez `demarrer` comme d'habitude : l'étape de téléchargement est alors instantanée.
