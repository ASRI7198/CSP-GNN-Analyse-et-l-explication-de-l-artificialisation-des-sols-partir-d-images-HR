# Détection de motifs d'artificialisation

Ce projet implémente la détection de motifs d'artificialisation à partir d'un graphe spatio-temporel à l'aide d'un Graphe Neuronal (GNN) : méthode Multi\_SPminer.

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
