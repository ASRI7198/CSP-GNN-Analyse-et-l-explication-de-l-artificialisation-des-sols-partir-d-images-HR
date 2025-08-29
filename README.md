# ANR Hérelles — Méthode hybride GNN + CSP pour l’analyse des changements environnementaux

## Contexte
Ce stage s’inscrit dans le cadre du projet **ANR Hérelles**, dont l’objectif est d’analyser et de modéliser les dynamiques de changements environnementaux à partir d’images satellitaires **à haute résolution**.

## Objectif
Développer une **méthode hybride** combinant des **Graph Neural Networks (GNN)** et des **problèmes de satisfaction de contraintes (CSP)** pour **détecter** et **interpréter** les changements liés à l’**artificialisation des sols**.

## Méthodologie (3 étapes)
1. **Définition de motifs géospatiaux** représentant des configurations typiques d’artificialisation.  
2. **Détection de motifs complexes** à l’aide des **GNN**.  
3. **Formalisation et résolution** de ces motifs via un **solveur CSP** afin **d’intégrer** et **vérifier** les **contraintes spatiales et temporelles**.

## Explicabilité
- **Explications factuelles** : décrivent les **causes des changements observés**.  
- **Explications contrefactuelles** : simulent les **évolutions qui auraient pu se produire** en l’absence de certains facteurs.

## Impact attendu
Ces capacités visent à **soutenir la gestion durable des territoires**, en apportant aux décideurs des **éléments d’interprétation** fiables et actionnables.

---

**Mots-clés :** GNN, CSP, motifs géospatiaux, artificialisation des sols, imagerie satellitaire haute résolution, explicabilité (facticielle & contrefactuelle).


# 1 - Segmentation et classification avec QGIS

Ce dépôt décrit **l’étape “Segmentation & Classification”** d’un projet d’occupation des sols sous **QGIS**.  
Il documente les données attendues, le flux de travail pas-à-pas, **les variables calculées**, **les classes étudiées**, ainsi que **les méthodes et résultats** utilisés dans notre étude.

---

## ✅ Prérequis

- **QGIS 3.28+** (ou version plus récente)
- Plugins recommandés (via *Extensions > Installer/Gérer les extensions…*):
  - **Orfeo Toolbox (OTB)** — segmentation et classification avancées  
    > Nécessite l’installation d’OTB puis la configuration dans *Traitements > Options > Fournisseurs > Orfeo Toolbox*.
  - **Semi-Automatic Classification Plugin (SCP)** *(optionnel)* — classification et évaluation
  - **SAGA/GRASS** *(optionnels)* — alternatives pour certaines étapes (segmentation, post-traitements)
- Données d’imagerie (ex. Sentinel-2, orthophotos…), **géoréférencées** et **projetées** dans un CRS métrique approprié (UTM local).

---

## 📁 Structure du projet

```
Images/                      # Imagerie d’entrée (GeoTIFF, JP2, etc.)
Vecteur Classes/             # Polygones d’entraînement (étiquetés), ex. classes_train.gpkg
Classes/                     # Style, tables de légende, codes classe (.csv, .qml)
Segmentation/                # Résultats de segmentation (raster ou vecteur)
Classification/              # Rasters classifiés, cartes finales, masques post-traités
Statistiques/                # Rapports: matrices de confusion, scores (OA, Kappa, F1), graphes
Segmentation et Classification.qgz   # Fichier projet QGIS préconfiguré
```

### Convention de nommage (recommandée)
- `Images/scene_YYYYMMDD.tif`
- `Vecteur Classes/classes_train.gpkg` (couche: `train_polys`)
- `Segmentation/segments_YYYYMMDD.gpkg` (couche: `segments`)
- `Classification/classif_RF700_YYYYMMDD.tif`
- `Statistiques/report_classif_YYYYMMDD.md`

---

## 🧭 Flux de travail (pas-à-pas)

### 1) Préparer l’imagerie (dossier `Images/`)
1. Déposer les rasters d’entrée (bandes empilées si possible).  
2. Vérifier le **CRS** et reprojeter si besoin (*Raster > Projections > Reprojeter…*).  
3. (Optionnel) Découper à l’emprise d’étude (*Traitements > GDAL > Extraction > Découper un raster par emprise*).

**Résultat attendu :** `Images/scene_*.tif`

---

### 2) Créer les classes d’entraînement (dossier `Vecteur Classes/`)
1. Créer un GeoPackage `classes_train.gpkg` contenant une couche polygonale `train_polys`.  
2. Champs recommandés :
   - `class_id` (entier) — code numérique de classe
   - `class_name` (texte) — libellé (ex. `Zones urbanisées`, `Eaux continentales`, etc.)
   - `fold` (entier, optionnel) — 0 = train, 1 = validation (pour l’évaluation)
3. Numériser des **polygones homogènes** par classe couvrant la variabilité spectrale.

**Résultat attendu :** `Vecteur Classes/classes_train.gpkg`

---

### 3) Segmentation (dossier `Segmentation/`)

**Contexte de l’étude**  
Nous avons appliqué la segmentation sur une série d’images satellitaires à l’aide du plugin **Orfeo Toolbox (OTB)**, intégré à **QGIS**. Quatre méthodes proposées par OTB ont été testées :

- **Mean Shift** : regroupe les pixels similaires en fonction de leur couleur et de leur proximité spatiale. Utile pour détecter des objets bien définis.  
- **Connected Components (CC)** : identifie les zones de pixels connectés ayant la même valeur. Méthode simple mais sensible au bruit.  
- **Watershed** : interprète l’image comme une surface topographique et sépare les régions selon le principe des bassins versants. Utile pour distinguer des objets collés.  
- **Profiles** : utilise les variations d’intensité (profils radiométriques) pour segmenter l’image. Adaptée aux structures linéaires comme les routes ou les rivières.

**Méthode retenue** : **Mean Shift**, en raison de ses performances plus robustes pour la détection des objets dans nos données.

**Export** : Les segments sont vectorisés en polygones (`segments_*.gpkg`) pour l’analyse géospatiale.

---

### 4) Variables calculées par segment (géométriques & contextuelles)

Après la segmentation, nous avons calculé un ensemble d’**attributs géométriques et contextuels** via l’outil **“Calculer les statistiques”** de QGIS et des traitements associés.  
Les variables retenues sont listées ci‑dessous :

| Variable                 | Description                                                                 | Unité typique                 |
|--------------------------|-----------------------------------------------------------------------------|-------------------------------|
| `DN`                     | Identifiant unique du polygone                                              | — (identifiant)               |
| `year`                   | Année d’acquisition                                                         | Année (ex. 2019, 2024)        |
| `Aire`                   | Surface totale du polygone                                                  | m²                            |
| `Perimeter`              | Longueur totale du contour du polygone                                      | m                             |
| `Largeur`                | Largeur maximale du polygone                                                | m                             |
| `Hauteur`                | Hauteur maximale du polygone                                                | m                             |
| `Rectangularity`         | Mesure de la “rectangularité”                                               | Sans unité (ratio)            |
| `Elongation`             | Mesure de l’étirement du polygone                                           | Sans unité (ratio)            |
| `Indice_Miller`          | Indice de compacité (Miller)                                                | Sans unité (ratio)            |
| `Multipolygone`          | Géométrie multipolygone                                                     | — (objet géométrique)         |
| `Centroid`               | Centre de gravité géométrique                                               | Coordonnées (x, y)            |
| `Nbr_Voisins`            | Nombre de polygones voisins adjacents                                       | Nombre entier                 |
| `Surf_Voisins`           | Somme des surfaces des polygones voisins                                    | m²                            |
| `Pix_Mean`               | Moyenne des valeurs de pixels contenus dans le polygone                     | Valeur numérique              |
| `Pix_Std`                | Écart type des valeurs de pixels contenus dans le polygone                  | Valeur numérique              |
| `Pix_Var`                | Variance des valeurs de pixels contenus dans le polygone                    | Valeur numérique              |

> Remarque : adaptez les noms de champs à vos couches (ex. `seg_id`, `mean_B2`, etc.) si vous extrayez des statistiques zonales par bande.

**Résultat attendu :** `Segmentation/segments_*.gpkg` enrichi avec ces variables.

---

### 5) Liste des classes étudiées (Niveau 1 — 2019, Montpellier Méditerranée Métropole)

Le jeu d’occupation du sol (1994–2023, 48 classes au niveau 4) a été **agrégé au niveau 1** pour notre analyse 2019. Les **8 classes** retenues sont :

| # | Nom de classe | Description |
|---|---------------|-------------|
| 1 | **Chantiers** | Zones de construction active (bâtiments, infrastructures en travaux) |
| 2 | **Eaux continentales** | Plans d’eau naturels ou artificiels (lacs, rivières, réservoirs) |
| 3 | **Espaces ouverts, sans ou avec peu de végétation** | Terrains non bâtis à végétation rare (sols nus, parkings, terrains vagues) |
| 4 | **Forêts** | Zones boisées à couvert végétal dense |
| 5 | **Réseaux routier et ferroviaire et espaces associés** | Infrastructures de transport et leurs abords (routes, gares, talus) |
| 6 | **Zones agricoles** | Terres cultivées, pâturages, vergers |
| 7 | **Zones de loisirs** | Espaces récréatifs (parcs, stades, terrains de golf) |
| 8 | **Zones urbanisées** | Bâtiments, quartiers résidentiels/commerciaux, zones industrielles |

Placez votre table de correspondance (`Classes/classes.csv`) pour lier `class_id`, `class_name` et une **couleur** QGIS.

---

### 6) Préparer l’échantillonnage d’apprentissage
Associer les **étiquettes** (`class_id`) aux segments :

1. *Vecteur > Outils de géotraitement > Intersection* entre `train_polys` et `segments`.  
2. (Option) Dissoudre par `seg_id` en gardant la **classe majoritaire** si plusieurs classes touchent le même segment.  
3. Conserver deux ensembles si souhaité : `fold=0` (train) et `fold=1` (validation).

**Résultat attendu :** table d’échantillons avec descripteurs + `class_id`.

---

### 7) Classification supervisée (OTB/SCP)

La classification repose sur l’image segmentée et un jeu d’entraînement annoté. Après extraction des caractéristiques, un **modèle** (p. ex. **Random Forest** ou **SVM**) est **entraîné** puis **appliqué** pour produire une carte classifiée (par segment ou par pixel).

**Modèles testés et performances (↑ = meilleur)**

| Modèle                     | Accuracy | Précision | Rappel | F1-score |
|---------------------------|---------:|----------:|-------:|---------:|
| **Random Forest (700 arbres)** | **0,81** | **0,78** | **0,81** | **0,79** |
| Random Forest (100 arbres) | 0,551 | 0,54 | 0,55 | 0,52 |
| Boosting                   | 0,364 | 0,13 | 0,36 | 0,18 |
| KNN                        | 0,364 | 0,13 | 0,36 | 0,18 |
| Naive Bayes                | 0,223 | 0,27 | 0,22 | 0,21 |
| SVM                        | 0,213 | 0,28 | 0,21 | 0,19 |

**Meilleur modèle** : **Random Forest (700 arbres)** — performances les plus élevées et segmentation/classification visuellement cohérentes.

**Sorties attendues :**
- `Classification/classif_RF700_*.tif` (raster de classes)
- `Statistiques/` (matrices de confusion, courbes, rapport)

---

### 8) Post-traitements (optionnels)
- **Filtre de majorité / lissage** pour réduire le bruit sel-poivre
- **Morphologie** (ou *r.neighbors* via GRASS)
- **Vectorisation** des classes d’intérêt (*Raster > Conversion > Polygones à partir de raster*)

**Résultat attendu :** produits cartographiques lisibles (raster + vecteur).

---

## 📊 Évaluation & illustrations

- **Échantillons de validation** : polygones/points indépendants (`fold=1`).  
- **Métriques** : Accuracy, Précision, Rappel, **F1‑score** (cf. tableau ci‑dessus).  
- **Illustrations** (déposez vos figures ici et mettez à jour les chemins) :  
  - `Segmentation/seg1.jpg`, `Segmentation/seg2.jpg` — exemples de **segmentation Mean Shift**  
  - `Classification/image-segmenter.jpg`, `Classification/image-colore.jpg` — **(a) Segmentation / (b) Classification**  
  - `Classes/classes.jpg` — légende des classes

---

## 🎨 Styles & légende (dossier `Classes/`)

- `classes.csv` : mapping `class_id,class_name,color` pour **8 classes niveau 1** ci‑dessus.  
- Style QGIS (`.qml`) appliqué au raster de classification pour une palette cohérente.

---

## 🚀 Démarrage rapide

1. **Ouvrir** `Segmentation et Classification.qgz` dans QGIS.  
2. Vérifier les **chemins relatifs**.
3. Charger `Images/scene_*.tif` et `Vecteur Classes/classes_train.gpkg`.  
4. Lancer la **segmentation** (OTB > *Mean Shift*, méthode retenue), extraire les **variables**, **entraîner** le modèle (RF700) et **classer**.  
5. Exporter les **rapports** dans `Statistiques/` et la carte finale dans `Classification/`.

---

## 🧪 Conseils pratiques

- **Équilibrer** les échantillons par classe (surface/nb de segments).
- Ajuster la **granularité** des segments pour l’échelle des objets.
- Séparer **entraînement** et **validation** (champ `fold`).
- Sauvegarder modèles et paramètres pour la **reproductibilité**.

---

## 📄 Licence / Données

- Données d’occupation du sol : **Montpellier Méditerranée Métropole (1994–2023)**.  
  Pour cette étude, **8 classes niveau 1** ont été utilisées pour **2019**.  
- Indiquez ici la licence des données et du code (ex. MIT, CC‑BY‑SA).

---

## 🔧 Dépannage

- OTB non détecté : configurez le chemin dans *Traitements > Options > Orfeo Toolbox*.
- Segmentation trop fine/grossière : ajustez les paramètres Mean‑Shift (ou testez CC/Watershed/Profiles).
- Classes confondues : ajoutez des **échantillons**, des **indices** (NDVI/NDBI/NDWI), ou testez un autre algorithme.



<!-- ===== Hero / Header ===== -->
<div align="center">

# 2 - Extraction et Analyse de Graphes Spatio‐Temporels

</div>

<p align="center">
  <img alt="divider" src="https://img.shields.io/badge/Python-%3E%3D3.8-informational" />
  <img alt="geopandas" src="https://img.shields.io/badge/GeoPandas-usage-blue" />
  <img alt="networkx" src="https://img.shields.io/badge/NetworkX-graphs-blue" />
  <img alt="shapely" src="https://img.shields.io/badge/Shapely-geometry-blue" />
  <img alt="pandas" src="https://img.shields.io/badge/Pandas-dataframe-blue" />
  <img alt="matplotlib" src="https://img.shields.io/badge/Matplotlib-visualization-blue" />
</p>

---

<details>
<summary><strong>📑 Sommaire</strong></summary>

- [2 - Extraction et Analyse de Graphes Spatio‐Temporels](#2---extraction-et-analyse-de-graphes-spatio-temporels)
  - [Arborescence du projet](#arborescence-du-projet)
  - [Installation et dépendances](#installation-et-dépendances)
  - [Description des fichiers](#description-des-fichiers)
  - [Stockage des données et résultats](#stockage-des-données-et-résultats)
  - [Usage](#usage)
</details>

---

Cette étape vise à :

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
├── Graphes spatiaux/           # GraphML produits pour chaque date (local)
├── Graphes Spatio-Temporelles/ # GraphML produits pour les transitions (local)
└── Statistiques/               # Données et scripts statistiques (stockés sur Google Drive)
```

---

## Installation et dépendances

1. **Python >= 3.8**
2. Installer les packages requis :
   ```bash
   pip install geopandas networkx shapely pandas matplotlib
   ```

---

## Description des fichiers

### 1. Data_preparation.py

- **To_Json(path, nams)** : lit un GeoPackage via GeoPandas et exporte le contenu en CSV (*Grabels*\*.csv\*).
- **Bloc principal** : itère sur une liste de suffixes de dates, convertit chacun des fichiers GeoPackage en CSV.

### 2. Noeud.py

- **Classe `Noeud`** :
  - Attributs : DN, year, Aire, Perimeter, Largeur, Hauteur, Rectangularity, I_Miller, centroid, mean, std, variance, classe.
  - Méthodes :
    - `Polygon_Elongation()` : calcule l’élongation (rapport côté long / côté court).
    - `nombre_voisins_adjacents(multipolygones)` : compte les polygones adjacents (touchant).
    - `surface_cumulee_voisins(multipolygones)` : somme des surfaces des voisins adjacents.
    - `compute_all(multipolygones)` : exécute toutes les méthodes de calcul d’attributs.

### 3. Relation_spasital.py

- **`Adjacence(graphe)`** :
  - Pour chaque paire de nœuds, teste si leurs géométries se touchent (Shapely `touches`).
  - Ajoute une arête avec `relation='Adjacence'` si c’est le cas.

### 4. Relation_temporelle.py

- **Utilitaires** :
  - `getDistance(attr1, attr2)` : distance euclidienne entre deux centroïdes (*string* → coordonnées).
  - `max_polygon_length(attr)` : diamètre maximal du MultiPolygon.
  - `Mon_function(attr1, attr2)` : score de similarité moyenne sur les attributs `{Aire, Perimeter, Rectangularity, I_Miller}`.
- **Relations** :
  - `Scission(G1, G2)` : lie nœuds de G1 à G2 si plusieurs fragments d’un même polygone original apparaissent (score 0<…≤0.9 et somme de surfaces proche à 5 %).
  - `Fusion(G1, G2)` : analogue à `Scission` mais pour plusieurs nœuds de G1 fusionnant en un de G2.
- **`Copy_Nodes(G1, G2)`** : initialise un MultiDiGraph contenant tous les nœuds annotés par année.

### 5. Relations_filiation.py

- Même structure d’utilitaires (`getDistance`, `max_polygon_length`, `Mon_function`).
- **`Continuation(G1, G2)`** : relie si un même polygone persiste d’une date à l’autre (score >0.9).
- **`Dérivation(G1, G2)`** : relie si un polygone se transforme en plusieurs (score 0–0.9).
- **`get_attributes(attr)`** : affiche à l’écran les attributs d’un nœud (debug).
- **`Copy_Nodes(G1, G2)`** : identique à celle de `Relation_temporelle.py`, pour initialiser les nœuds.

### 6. Functions.py

- **Chargement de CSV** : fonctions (`Geometry`, `Classes`, `DN`, `Area`, `Perimeter`, `Compacité`, `Width`, `Height`, `Rectangularity`, `mean`, `std`, `variance`) qui renvoient des listes issues des colonnes du CSV.
- **`Year(path)`** : extrait l’année et le mois du nom de fichier (*Grabels_XX_YYYY.csv*).
- **`Create_Noeuds(path)`** :
  1. Lit le CSV et crée un `Noeud` par ligne.
  2. Calcule automatiquement les attributs (*compute_all*).
- **`Create_Graph(noeuds)`** :
  - Construit un graph NetworkX non-orienté avec chaque `Noeud` comme nœud annoté de ses attributs.
  - Applique `Relation_spasital.Adjacence` pour ajouter les arêtes spatiales.
- **`Create_Graphe_spatio_temporel(G1, G2)`** :
  1. Génère un MultiDiGraph initialisé avec tous les nœuds de G1 et G2 (clé=(node_id, year)).
  2. Copie les arêtes spatiales de G1, G2 en les annotant de la date.
  3. Applique `Scission`, `Fusion`, `Dérivation`, `Continuation` pour relier G1⇄G2.
- **`get_last_year` / `get_first_year`** : utilitaires pour extraire la plage de dates.
- **`Create_Graphe_spatio_temporel_2(G_st1, G_st2)`** : variante qui ne considère que les entités de transition entre dernière année de G_st1 et première année de G_st2.
- **`Stocker_Graph_GraphML(G, name, index)`** :
  - Exporte le graphe en GraphML (XML) dans `Graphes spatiaux/` (index=0) ou `Graphes Spatio-Temporelles/` (index=1).
- **`Read_GraphML(path, name)`** : lit un fichier `.graphml.xml` et retourne un objet NetworkX.

### 7. Main.py

- Définit des listes de suffixes de dates (`nams`).
- **`traitement_Creat_GS()`** : pour chaque CSV, crée le graphe spatial et l’exporte.
- **`traitement_Read_GS()`** : charge tous les graphes spatiaux exportés.
- **`traitement_Read_GST(nams_st)`** : charge tous les graphes spatio-temporels.
- **`traitement_Creat_GST()`** : génère et stocke les premiers graphes spatio-temporels à partir de paires successives de graphes spatiaux.
- **`traitement_Creat_GST_2(nams_st)`** : génère des graphes spatio-temporels plus larges (enchaînements de plusieurs périodes).
- **`__main__`** : exécute la chaîne complète de création et de stockage.

---

### Stockage des données et résultats

1. Les graphiques spatiaux et spatio‐temporels, ainsi que les exports statistiques, sont accessibles sur ce Google Drive :
https://drive.google.com/drive/folders/1yym5qWhOCaro-jY7DkBYTQwLnL5jsQqN?usp=sharing
2. Les répertoires Graphes spatiaux/ et Graphes Spatio-Temporelles/ contiennent les fichiers .graphml.xml générés localement.
3. Le dossier visualisation/ contient les résultats de visualisation (plots et cartes) pour chaque graphe spatial.

## Usage

1. **Préparez** vos GeoPackage dans le dossier `Statistiques/`.
2. **Lancez** :
   ```bash
   python Data_preparation.py
   python Main.py
   ```
3. **Consultez** les fichiers GraphML générés dans :
   - `Graphes spatiaux/`
   - `Graphes Spatio-Temporelles/`
4. **Affichez** les statistiques via :
   ```python
   from Function_GST import afficher_statistiques_gst
   afficher_statistiques_gst(votre_graphe_st)
   ```


<!-- ===== Hero / Header ===== -->
<div align="center">

# 3 - Détection de motifs d'artificialisation

</div>

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/Python-%3E%3D3.10-informational" />
  <img alt="GNN" src="https://img.shields.io/badge/GNN-Multi_SPminer-blue" />
  <img alt="NetworkX" src="https://img.shields.io/badge/Graphs-NetworkX-blue" />
  <img alt="Torch" src="https://img.shields.io/badge/Deep%20Learning-PyTorch-red" />
</p>

---

Cette étape implémente la détection de motifs d'artificialisation à partir d'un graphe spatio-temporel à l'aide d'un Graphe Neuronal (GNN) : méthode **Multi_SPminer**.

---

<details>
<summary><strong>📑 Sommaire</strong></summary>

- [3 - Détection de motifs d'artificialisation](#3---détection-de-motifs-dartificialisation)
  - [Structure du projet](#structure-du-projet)
  - [Description par dossier et fichier](#description-par-dossier-et-fichier)
  - [Données](#données)
  - [Prérequis et installation](#prérequis-et-installation)
</details>

---

## Structure du projet

Le dépôt est organisé en deux phases principales :

```
├── Embedding_phase/
│   ├── Generate_data/
│   │   ├── Generate_training.py
│   │   ├── Preprocess_attributes.py
│   │   ├── Pretreatment.ipynb
│   │   └── config.py
│   ├── MGCN/
│   │   ├── Embedding_Loss.py
│   │   └── Multi_GCN.py
│   └── Main/
│       ├── Analyze_Embeddings.ipynb
│       ├── Evaluation des embeddings.ipynb
│       ├── Test.py
│       ├── Train.py
│       └── main.py
├── Visualisation/
└── Search_phase/
    ├── Search.py
    └── search_test.ipynb
```

---

## Description par dossier et fichier

> ℹ️ **Remarque** — Les descriptions ci‑dessous détaillent le rôle **attendu** de chaque fonction compte tenu des noms de fichiers. Adaptez les intitulés si vos signatures diffèrent.

### 1) `Embedding_phase/Generate_data`

<details>
<summary><code>Generate_training.py</code> — génération du dataset supervision (paires de sous‑graphes A/B + labels)</summary>

#### Fonctions (attendues)
- `build_k_hop_subgraph(G, center_id, k, max_nodes)` : extrait le sous‑graphe **k‑hop** autour d’un nœud pivot, en bornant la taille maximale.
- `pair_label(subA, subB)` : calcule le **label** de la paire (ex. même motif / motif différent / type de relation).
- `generate_pairs(G, k, max_nodes, sampling, seed)` : itère sur le graphe spatio‑temporel pour produire des paires équilibrées A/B.
- `to_example(subG)` : convertit un sous‑graphe en **exemple** (features, edges, masque, meta).
- `save_dataset(examples, out_dir)` : sérialise le dataset (NPZ/JSON/Parquet) et l’index des paires.
- `load_dataset(path)` : charge un dataset généré pour ré‑entraînement ou test.

#### Entrées / Sorties
- **Entrées** : graphe spatio‑temporel `G`, paramètres `k`, `max_nodes`, stratégie `sampling`.
- **Sorties** : `{X, edge_index, y, meta}` par paire, fichiers sur disque (train/val/test).
</details>

<details>
<summary><code>Preprocess_attributes.py</code> — préparation des attributs de nœuds/arêtes</summary>

#### Fonctions (attendues)
- `load_graphml(path)` : lit un GraphML et retourne un (Multi)DiGraph NetworkX.
- `compute_node_features(G, columns)` : construit la **matrice d’attributs** des nœuds (aires, périmètres, compacités, etc.).
- `compute_edge_features(G, columns=None)` : (optionnel) construit des attributs d’arêtes (type relation, distance, année).
- `normalize_features(X, method="standard")` : standardisation/min‑max et sauvegarde des paramètres de normalisation.
- `save_features(X, path)` / `load_features(path)` : I/O des matrices d’attributs.
- `split_train_val_test(ids, ratios, seed)` : crée des splits reproductibles.

#### Entrées / Sorties
- **Entrées** : fichiers `.graphml.xml` ou `.csv` d’attributs.
- **Sorties** : matrices **X**, éventuelles **E**, index de splits.
</details>

<details>
<summary><code>Pretreatment.ipynb</code> — notebook d’orchestration du prétraitement</summary>

- Pipeline pas‑à‑pas : chargement des graphes, extraction features, normalisation, vérifications de qualité, export.
</details>

<details>
<summary><code>config.py</code> — configuration centralisée</summary>

#### Contenu (attendu)
- Hyperparamètres : `K_HOP`, `MAX_NODES`, `BATCH_SIZE`, `LR`, `EPOCHS`, `HIDDEN_DIMS`, `DROPOUT`.
- Chemins : `DATA_ROOT`, `OUT_DIR`, `LOG_DIR`, `CKPT_DIR`.
- Aléas & device : `SEED`, `DEVICE` (`"cpu"`/`"cuda"`).
</details>

### 2) `Embedding_phase/MGCN`

<details>
<summary><code>Embedding_Loss.py</code> — fonctions de perte pour l’apprentissage d’embeddings</summary>

#### Fonctions (attendues)
- `supervised_contrastive_loss(z, y, temperature=0.1)` : rapproche les embeddings de **même label**, éloigne les autres.
- `triplet_margin_loss(a, p, n, margin=1.0)` : ancre/positif/négatif pour structurer l’espace latent.
- `classification_loss(logits, y, weight=None)` : perte de classification (ex. BCE/CE) quand un classifieur est joint.
- `regularization(embeddings, l2=1e-5)` : pénalité L2/L1 sur les vecteurs latents.
</details>

<details>
<summary><code>Multi_GCN.py</code> — architecture du modèle MGCN</summary>

#### Eléments (attendus)
- `class MultiGCN(nn.Module)` : empilement de couches GCN/GAT/GIN (selon variante), pooling global (mean/max/attention).
- `forward(x, edge_index, batch=None, edge_attr=None)` : produit **embeddings** et/ou **logits**.
- `encode_subgraph(data)` : encodage d’un sous‑graphe en vecteur latent.
- `readout(node_embeddings, batch)` : agrégation par graphe (global pooling).
</details>

### 3) `Embedding_phase/Main`

<details>
<summary><code>Train.py</code> — boucle d’entraînement</summary>

#### Fonctions (attendues)
- `set_seed(seed)` : reproductibilité (torch, numpy, python).
- `build_loaders(dataset, batch_size, num_workers=0)` : DataLoaders train/val/test.
- `train_one_epoch(model, loader, optimizer, loss_fns, scheduler=None)` : passe avant, calcul des pertes multiples, rétropropagation.
- `evaluate(model, loader, metrics=("loss","auc","f1"))` : évalue et retourne un dictionnaire de métriques.
- `fit(cfg)` : orchestre **n** époques avec early‑stopping et sauvegarde de checkpoints.
- `save_checkpoint(state, path)` / `load_checkpoint(model, path)` : gestion des poids et de l’optimiseur.
</details>

<details>
<summary><code>Test.py</code> — inférence et export des embeddings</summary>

#### Fonctions (attendues)
- `load_model(cfg, ckpt_path)` : reconstruit le modèle et charge les poids.
- `infer_embeddings(model, loader)` : calcule les embeddings sur un split donné.
- `evaluate_embeddings(z, y, metrics=("auc","f1","acc"))` : métriques **downstream** (option régression logistique).
- `export_embeddings(z, meta, out_path)` : sauvegarde (npz/csv/parquet) pour analyse/recherche de motifs.
</details>

<details>
<summary><code>main.py</code> — point d’entrée</summary>

#### Fonctions / CLI (attendues)
- `parse_args()` : `--mode {train,test}`, `--config`, `--ckpt`, etc.
- `main_train(cfg)` / `main_test(cfg)` : lance l’un des deux workflows.
- `if __name__ == "__main__":` : dispatch vers **train** ou **test**.
</details>

<details>
<summary><code>Analyze_Embeddings.ipynb</code> & <code>Evaluation des embeddings.ipynb</code></summary>

- Visualisations (t‑SNE/UMAP), statistiques d’intra/inter‑classe, courbes ROC/PR, ablations.
</details>

### 4) `Visualisation/`

- Actifs de visualisation (courbes de perte, figures t‑SNE/UMAP), scripts/nb facultatifs pour tracer les résultats.

### 5) `Search_phase`

<details>
<summary><code>Search.py</code> — extraction des motifs d’artificialisation</summary>

#### Fonctions (attendues)
- `load_embeddings(path_or_dir)` : charge les vecteurs latents produits en phase d’embedding.
- `prepare_index(G, z, meta=None)` : indexe nœuds/sous‑graphes pour les requêtes (ex. faiss/annoy ou simple cosine).
- `score_subgraph(subG, z)` : attribue un **score** de motif (similarité, seuils).
- `search_patterns(G, z, top_k=50, thresholds=None)` : parcours/échantillonnage, scoring et **sélection** des meilleurs motifs.
- `postprocess(candidates, nms=True, overlap_thr=0.5)` : dédoublonnage/fusion de motifs proches.
- `export_json(results, out_path)` : écrit les motifs détectés (JSON) pour inspection et pour le CSP en aval.
</details>

<details>
<summary><code>search_test.ipynb</code> — démonstration de la recherche</summary>

- Notebook d’exemple : chargement des embeddings, lancement de `search_patterns`, visualisation rapide des motifs trouvés.
</details>

---

## Données

Les données produites par `generate_data` sont volumineuses (entre **2 Go** et **38 Go**).  
Le graphe spatio-temporel complet et les résultats des motifs d’artificialisation (ensemble de fichiers JSON, un par configuration de paramètres et données paires) sont disponibles dans le dossier partagé Drive :  
https://drive.google.com/drive/folders/1yym5qWhOCaro-jY7DkBYTQwLnL5jsQqN?usp=sharing

---

# Validation de motifs par CSP (Choco Solver)

Ce projet valide des **motifs** sur des **graphes spatio-temporels** via un **CSP** construit avec **Choco Solver**.  
Entrées : un graphe ST (JSON) et un ou plusieurs motifs (Java ou JSON).  
Sorties : les **occurrences** du motif (console et/ou export).

---

## Arborescence

```
.
├── pom.xml
├── .gitignore
├── src/
│   └── main/
│       └── java/
│           ├── Motifs/                      # (optionnel) motifs codés en Java
│           └── org/example/
│               ├── BuildResult.java         # structure & affichage des solutions
│               ├── CSPModelBuilder.java     # création variables & contraintes CSP
│               ├── Edge.java                # arête d’un motif (u, v, type)
│               ├── EdgeType.java            # SPATIAL / TEMPORAL / ...
│               ├── Inspect.java             # utilitaire d’inspection du graphe
│               ├── MotifJsonLoader.java     # chargement motif au format JSON
│               ├── Pattern_M.java           # exemple de motif en Java
│               ├── STGraph.java             # graphe spatio-temporel (noeuds, arêtes, attrs)
│               ├── STLoader.java            # loader du graphe (JSON → STGraph)
│               ├── SolveAllPatterns.java    # résolution d’une liste de motifs
│               └── SolvePattern.java        # résolution d’un motif unique
└── src/main/java/org/example/stgraph4.json  # exemple de graphe ST
```

> Astuce : déplacez les JSON dans `src/main/resources/` et chargez‐les via le **classpath**.

---

## Principe

1. **Chargement du graphe** (`STLoader` → `STGraph`).  
2. **Chargement du motif** :  
   - **Java** (ex. `Pattern_M.java`), ou  
   - **JSON** via `MotifJsonLoader`.  
3. **Construction du CSP** (`CSPModelBuilder`) :  
   - Variables : une par nœud du motif (domaine = candidats du graphe).  
   - Contraintes :
     - **Injectivité** (`AllDifferent`) : pas de réutilisation d’un même nœud.
     - **Spatiales** (`EdgeType.SPATIAL`) : voisinage/adjacence même couche.
     - **Temporelles** (`EdgeType.TEMPORAL`) : ordre strict sur le temps/couche.
     - (Optionnel) **filtres d’attributs** (type, aire, etc.).  
4. **Résolution** (Choco) → **occurrences** imprimées/exportées (`BuildResult`).

---

## Dépendances

- **JDK** 11+ (idéalement 17+)  
- **Maven** 3.8+  
- **Choco Solver** (déclaré dans `pom.xml`)  

---

## Installation

```bash
# À la racine du projet
mvn -q -DskipTests package
```

Le jar est généré dans `target/`. Vous pouvez aussi exécuter les classes `main` depuis l’IDE.

---

### 1) Inspecter un graphe
```bash
mvn -q exec:java   -Dexec.mainClass=org.example.Inspect   -Dexec.args="--graph src/main/java/org/example/stgraph4.json"
```

### 2) Résoudre **un motif**
- Motif défini en **Java** (ex. `Pattern_M`) :
```bash
mvn -q exec:java   -Dexec.mainClass=org.example.SolvePattern   -Dexec.args="--graph src/main/java/org/example/stgraph4.json --pattern M"
```

- Motif défini en **JSON** :
```bash
mvn -q exec:java   -Dexec.mainClass=org.example.SolvePattern   -Dexec.args="--graph src/main/java/org/example/stgraph4.json --motif chemin/vers/motif.json"
```

### 3) Résoudre **plusieurs motifs**
```bash
mvn -q exec:java   -Dexec.mainClass=org.example.SolveAllPatterns   -Dexec.args="--graph src/main/java/org/example/stgraph4.json --limit 100"
```
---

## Ajouter un motif

- **En Java** : créer `Pattern_X.java` dans `Motifs/` (nœuds, arêtes typées, filtres).  
- **En JSON** : créer `motif_X.json` (structure ci-dessus) et le charger via `MotifJsonLoader`.

---


