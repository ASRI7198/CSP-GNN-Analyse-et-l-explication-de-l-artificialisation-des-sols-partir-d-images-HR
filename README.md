# 2 - Extraction et Analyse de Graphes Spatio‐Temporels

Cette étape vise à :

- Préparer et convertir des données géographiques (formats GeoPackage) vers des CSV exploitables.
- Créer des graphes spatiaux à partir de caractéristiques de polygones (aires, périmètres, etc.).
- Générer des graphes spatio‐temporels en combinant deux graphes spatiaux successifs et en détectant des relations (scission, fusion, dérivation, continuation).
- Exporter et lire des graphes en format GraphML.
- Calculer et afficher des statistiques sur les graphes produits.

---

## Arborescence du projet

```
├── function/                   # Code métier principal
│   ├── Functions.py            # Création de nœuds et graphes spatiaux / spatio‐temporels
│   └── Function_GST.py         # Affichage et calcul de statistiques sur les graphes
├── relation/                   # Détection des relations et préparation des données
│   ├── Relation_spasital.py    # Adjacence spatiale (Shapely touches)
│   ├── Relation_temporelle.py  # Scission et Fusion entre deux dates
│   ├── Relations_filiation.py  # Continuation et Dérivation
│   ├── Data_preparation.py     # Conversion GeoPackage → CSV
│   └── Noeud.py                # Classe Noeud et calcul d’attributs
├── pretreatment/               # Orchestration et prétraitement global
│   ├── Main.py                 # Script principal créant et stockant les graphes
│   └── test_GST.py             # (exemple de test ou de script statistique additionnel)
├── Graphes spatiaux/           # GraphML produits pour chaque date (local)
├── Graphes Spatio‑Temporelles/ # GraphML produits pour les transitions (local)
└── Statistiques/               # Données et scripts statistiques (stockés sur Google Drive)
```

---

## Installation et dépendances

1. **Python >= 3.8**
2. Installer les packages requis :
   ```bash
   pip install geopandas networkx shapely pandas matplotlib
   ```

---

## Description des fichiers

### 1. Data_preparation.py

- **To_Json(path, nams)** : lit un GeoPackage via GeoPandas et exporte le contenu en CSV (*Grabels*\*.csv\*).
- **Bloc principal** : itère sur une liste de suffixes de dates, convertit chacun des fichiers GeoPackage en CSV.

### 2. Noeud.py

- **Classe `Noeud`** :
  - Attributs : DN, year, Aire, Perimeter, Largeur, Hauteur, Rectangularity, I_Miller, centroid, mean, std, variance, classe.
  - Méthodes :
    - `Polygon_Elongation()` : calcule l’élongation (rapport côté long / côté court).
    - `nombre_voisins_adjacents(multipolygones)` : compte les polygones adjacents (touchant).
    - `surface_cumulee_voisins(multipolygones)` : somme des surfaces des voisins adjacents.
    - `compute_all(multipolygones)` : exécute toutes les méthodes de calcul d’attributs.

### 3. Relation_spasital.py

- **`Adjacence(graphe)`** :
  - Pour chaque paire de nœuds, teste si leurs géométries se touchent (Shapely `touches`).
  - Ajoute une arête avec `relation='Adjacence'` si c’est le cas.

### 4. Relation_temporelle.py

- **Utilitaires** :
  - `getDistance(attr1, attr2)` : distance euclidienne entre deux centroïdes (*string* → coordonnées).
  - `max_polygon_length(attr)` : diamètre maximal du MultiPolygon.
  - `Mon_function(attr1, attr2)` : score de similarité moyenne sur les attributs `{Aire, Perimeter, Rectangularity, I_Miller}`.
- **Relations** :
  - `Scission(G1, G2)` : lie nœuds de G1 à G2 si plusieurs fragments d’un même polygone original apparaissent (score 0<…≤0.9 et somme de surfaces proche à 5 %).
  - `Fusion(G1, G2)` : analogue à `Scission` mais pour plusieurs nœuds de G1 fusionnant en un de G2.
- **`Copy_Nodes(G1, G2)`** : initialise un MultiDiGraph contenant tous les nœuds annotés par année.

### 5. Relations_filiation.py

- Même structure d’utilitaires (`getDistance`, `max_polygon_length`, `Mon_function`).
- **`Continuation(G1, G2)`** : relie si un même polygone persiste d’une date à l’autre (score >0.9).
- **`Dérivation(G1, G2)`** : relie si un polygone se transforme en plusieurs (score 0–0.9).
- **`get_attributes(attr)`** : affiche à l’écran les attributs d’un nœud (debug).
- **`Copy_Nodes(G1, G2)`** : identique à celle de `Relation_temporelle.py`, pour initialiser les nœuds.

### 6. Functions.py

- **Chargement de CSV** : fonctions (`Geometry`, `Classes`, `DN`, `Area`, `Perimeter`, `Compacité`, `Width`, `Height`, `Rectangularity`, `mean`, `std`, `variance`) qui renvoient des listes issues des colonnes du CSV.
- **`Year(path)`** : extrait l’année et le mois du nom de fichier (*Grabels_XX_YYYY.csv*).
- **`Create_Noeuds(path)`** :
  1. Lit le CSV et crée un `Noeud` par ligne.
  2. Calcule automatiquement les attributs (*compute_all*).
- **`Create_Graph(noeuds)`** :
  - Construit un graph NetworkX non‑orienté avec chaque `Noeud` comme nœud annoté de ses attributs.
  - Applique `Relation_spasital.Adjacence` pour ajouter les arêtes spatiales.
- **`Create_Graphe_spatio_temporel(G1, G2)`** :
  1. Génère un MultiDiGraph initialisé avec tous les nœuds de G1 et G2 (clé=(node_id, year)).
  2. Copie les arêtes spatiales de G1, G2 en les annotant de la date.
  3. Applique `Scission`, `Fusion`, `Dérivation`, `Continuation` pour relier G1⇄G2.
- **`get_last_year` / `get_first_year`** : utilitaires pour extraire la plage de dates.
- **`Create_Graphe_spatio_temporel_2(G_st1, G_st2)`** : variante qui ne considère que les entités de transition entre dernière année de G_st1 et première année de G_st2.
- **`Stocker_Graph_GraphML(G, name, index)`** :
  - Exporte le graphe en GraphML (XML) dans `Graphes spatiaux/` (index=0) ou `Graphes Spatio‑Temporelles/` (index=1).
- **`Read_GraphML(path, name)`** : lit un fichier `.graphml.xml` et retourne un objet NetworkX.

### 7. Main.py

- Définit des listes de suffixes de dates (`nams`).
- **`traitement_Creat_GS()`** : pour chaque CSV, crée le graphe spatial et l’exporte.
- **`traitement_Read_GS()`** : charge tous les graphes spatiaux exportés.
- **`traitement_Read_GST(nams_st)`** : charge tous les graphes spatio‑temporels.
- **`traitement_Creat_GST()`** : génère et stocke les premiers graphes spatio‑temporels à partir de paires successives de graphes spatiaux.
- **`traitement_Creat_GST_2(nams_st)`** : génère des graphes spatio‑temporels plus larges (enchaînements de plusieurs périodes).
- **`__main__`** : exécute la chaîne complète de création et de stockage.

---

### Stockage des données et résultats

1. Les graphiques spatiaux et spatio‐temporels, ainsi que les exports statistiques, sont accessibles sur ce Google Drive :
https://drive.google.com/drive/folders/1yym5qWhOCaro-jY7DkBYTQwLnL5jsQqN?usp=sharing
2. Les répertoires Graphes spatiaux/ et Graphes Spatio‑Temporelles/ contiennent les fichiers .graphml.xml générés localement.
3. Le dossier visualisation/ contient les résultats de visualisation (plots et cartes) pour chaque graphe spatial.

## Usage

1. **Préparez** vos GeoPackage dans le dossier `Statistiques/`.
2. **Lancez** :
   ```bash
   python Data_preparation.py
   python Main.py
   ```
3. **Consultez** les fichiers GraphML générés dans :
   - `Graphes spatiaux/`
   - `Graphes Spatio‑Temporelles/`
4. **Affichez** les statistiques via :
   ```python
   from Function_GST import afficher_statistiques_gst
   afficher_statistiques_gst(votre_graphe_st)
   ```

# 3 - Détection de motifs d'artificialisation

Cette étape implémente la détection de motifs d'artificialisation à partir d'un graphe spatio-temporel à l'aide d'un Graphe Neuronal (GNN) : méthode Multi\_SPminer.

## Structure du projet

Le dépôt est organisé en deux phases principales :

### 1. Embedding\_phase

Ce dossier contient les sous-modules suivants :

* **generate\_data** : génère les données de sous-graphes A et B ainsi que leurs labels, en utilisant un nombre de hops (K-hop) et une taille maximale de graphe.
* **MGCN** : définition de l’architecture du modèle MGCN et de la fonction de perte associée.
* **main** : script principal (`main.py`) qui permet de lancer le programme, avec deux modes :

  * `train` : pour l’entraînement du modèle.
  * `test` : pour l’évaluation et l’analyse.
* **embeddings\_analysis** : calcul et statistiques des embeddings produits.
* **evaluation** : évaluation des embeddings par régression logistique.
* **visualisation** : génération des courbes de perte (train et validation) par epoch.

### 2. Search\_phase

Ce dossier contient :

* **search.py** : fonctions pour l’extraction des motifs d’artificialisation.
* **search\_test.py** : script pour appliquer ces fonctions sur le graphe spatio-temporel.
* **update\_json.py** : utilitaire pour modifier ou enrichir les fichiers JSON de résultats (ajout d’attributs, réglages des paramètres, etc.).

## Données

Les données produites par `generate_data` sont volumineuses (entre 2 Go et 38 Go).

Le graphe spatio-temporel complet et les résultats des motifs d’artificialisation (ensemble de fichiers JSON, un par configuration de paramètres et données paires) sont disponibles dans le dossier partagé Drive : https://drive.google.com/drive/folders/1yym5qWhOCaro-jY7DkBYTQwLnL5jsQqN?usp=sharing.

## Prérequis et installation

1. Créez et activez un environnement Python :

   ```bash
   conda create -n mon_env python=3.10
   conda activate mon_env
   ```

## Notes complémentaires

* J’ai développé l’intégralité du code en m’inspirant de plusieurs dépôts GitHub existants ; l’architecture et les fonctionnalités ont été conçues et optimisées spécifiquement pour ce projet.




