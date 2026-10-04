# tp-odoo : environnement de TP

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

Adresse du dépôt (public, aucun compte GitHub nécessaire pour le télécharger) :
**<https://github.com/M2P-git/tp-odoo>**

![QR code du dépôt](qr-tp-odoo.png)

**Avec Git** (conseillé), dans un dossier simple, par exemple `C:\cours` :

```bash
git clone https://github.com/M2P-git/tp-odoo.git
cd tp-odoo
```

Git n'est pas installé ? Windows : `winget install --id Git.Git -e` (ou <https://git-scm.com/download/win>) ;
macOS : `xcode-select --install` ; Linux : `sudo apt install git`. Fermez puis rouvrez le terminal, puis `git --version`.

**Sans Git** : bouton vert **Code → Download ZIP** sur la page GitHub, ou, dans PowerShell :

```powershell
Invoke-WebRequest https://github.com/M2P-git/tp-odoo/archive/refs/heads/main.zip -OutFile tp-odoo.zip
Expand-Archive tp-odoo.zip -DestinationPath .
```

Évitez les dossiers synchronisés (OneDrive, Google Drive).

### À chaque séance : revenir exactement à la version de la séance

Chaque séance, l'enseignant publie la version du jour (le fichier `SEANCE` indique son numéro ; elle contient
la correction des exercices des séances précédentes). **Cette opération efface vos modifications locales** et recrée Odoo :

| Windows | macOS / Linux |
|---|---|
| Double-cliquez sur **`mettre-a-jour.cmd`** | `./mettre-a-jour.sh` |

Ce que fait le fichier (vous pouvez aussi taper ces commandes vous-même, dans le dossier `tp-odoo`) :

```bash
git fetch origin --tags         # récupère les nouveautés publiées
git reset --hard origin/main    # remplace vos fichiers par ceux de la séance
git clean -fd                   # supprime les fichiers en trop
docker compose down -v          # efface l'ancien Odoo
demarrer.cmd                    # (ou ./demarrer.sh) recrée Odoo avec la configuration de la séance
```

Besoin d'une séance précise (séance manquée) : `mettre-a-jour.cmd seance-02` (étiquettes `seance-01`, `seance-02`, ...).
Voulez-vous garder un fichier modifié ? **Copiez-le hors du dossier avant** de mettre à jour.

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
| Acteurs internes | Sara Alaoui (commerciale), Hamza Tazi (magasinier), Leïla Benjelloun (acheteuse), Driss Amrani (comptable) |
| Clients | `C001` Nova Conseil (contact Yassine), `C002` École Sigma (Karim), `C003` MediTech (Ghita) |
| Fournisseurs | `F01` TechRoute (routeur 780 MAD, 5 jours), `F02` DockPro, `F03` Rapidis (routeur 950 MAD, 2 jours) |
| Produits suivis en stock | `P-R10` Routeur Pro R10 (1 200 MAD, **6 en stock**), `P-D02` Station d'accueil D2 (450 MAD, 8 en stock) |
| Ventes | `CO104` Nova Conseil, 10 routeurs, **confirmée**, livraison en attente ; `CO105` École Sigma, 2 routeurs, **devis** ; `CO106` MediTech, 3 stations, confirmée |
| Réapprovisionnement | Règle `P-R10` : minimum 3, maximum 12, déclenchement manuel |
| CRM | Campagnes *Webinaire* et *Salon*, **10 pistes importées telles quelles** (dont 2 doublons volontaires), 2 activités planifiées |
| À partir de la séance 4 | Application **Fabrication** installée ; composants `P-UC5` Unité centrale (2 en stock, numéros `UC5-0001` et `UC5-0002`), `P-E24` Écran 24 pouces (6, `E24-0001` à `E24-0006`), `P-K01` Kit clavier et souris (10) ; produit fini `P-W1` Poste de travail Pro W1 (6 900 MAD, suivi par numéro de série, **sans nomenclature** : c'est l'exercice) ; devis `CO107` MediTech, 4 postes |

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

## 7 bis. S'exercer sur sa propre instance Odoo

| Option | Pour qui | Remarques |
|---|---|---|
| **Ce dépôt (Docker)** | Tout le monde | Identique à la classe. `reinitialiser` repart d'un Odoo neuf. |
| **Odoo Online** (<https://www.odoo.com>) | Ceux qui veulent voir l'édition hébergée | Essai gratuit de 15 jours pour les formules payantes, ou formule gratuite « une seule application » (insuffisante pour CRM + Ventes + Achats + Inventaire). Importez ensuite `data/import-odoo/contacts.csv` et `produits.csv` (menu **Importer des enregistrements** d'une liste). Ne saisissez que des données fictives. |

## 7 ter. Facultatif : la grille d'applications d'Odoo Online dans la version Community

La version Community arrive sur *Discussion* et propose un petit menu déroulant ; Odoo Online affiche une grille d'icônes plein écran.
Le module communautaire **Web Responsive** (OCA) offre la même grille. Dans le dossier du dépôt :

```bash
git clone --depth 1 --branch 19.0 --filter=blob:none --sparse https://github.com/OCA/web.git oca-web
cd oca-web && git sparse-checkout set web_responsive && cd ..
cp -r oca-web/web_responsive extra-addons/        # Windows : xcopy /e /i oca-web\web_responsive extra-addons\web_responsive
docker compose restart odoo
```

Puis dans Odoo : activez le **mode développeur** (Paramètres, en bas de page), menu **Apps → Mettre à jour la liste des Apps**,
cherchez **Web Responsive** (en retirant le filtre « Apps ») et cliquez sur **Activer**. Le dossier `extra-addons/` est ignoré par Git :
`mettre-a-jour` ne l'efface pas (mais recrée la base : refaites la dernière étape).

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
