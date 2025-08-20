# Chemins vers les différents fichiers de données d'entraînement générés avec différents paramètres k-hop
DATA_PATH_8 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_500_pairs_8_k-hop.pt"
DATA_PATH_6 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_500_pairs_6_k-hop.pt"
DATA_PATH_4 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_500_pairs_4_k-hop.pt"
DATA_PATH_5 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_2000_pairs_5_k-hop.pt"
DATA_PATH_8_2 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_1000_pairs_8_k-hop.pt"
DATA_PATH_10 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_500_pairs_10_k-hop.pt"
DATA_PATH_6_2 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_1000_pairs_6_k-hop.pt"
DATA_PATH_12 = "/home/rida/GNN/Embedding_phase/Training_data/train_data_300_pairs_12_k-hop.pt"


# Chemin où je sauvegarde le meilleur modèle entraîné
MODEL_SAVE_PATH_8_2 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_1000_pairs_8_k-hop_16.pth"
MODEL_SAVE_PATH_14 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_14_k-hop_64.pth"
MODEL_SAVE_PATH_10 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_10_k-hop_16.pth"
MODEL_SAVE_PATH_5 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_2000_pairs_5_k-hop_16.pth"
MODEL_SAVE_PATH_6_2 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_1000_pairs_6_k-hop_16.pth"
MODEL_SAVE_PATH_8 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_8_k-hop_32.pth"
MODEL_SAVE_PATH_4 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_4_k-hop_32.pth"
MODEL_SAVE_PATH_6 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_6_k-hop_64.pth"
MODEL_SAVE_PATH_12 = "/home/rida/GNN/Embedding_phase/models/best_mgcn_order_embedding_500_pairs_12_k-hop_16.pth"

# Chemin vers le fichier GraphML de mon graphe spatio-temporel principal
GST_DATA_PATH = "/home/rida/GNN/Graphe Spatio-Temporel/GST_Grabels.graphml.xml"

# Dictionnaire des hyperparamètres utilisés pour l'entraînement de mon modèle
HYPERPARAMETERS = {
    'batch_size': 8,
    'learning_rate': 1e-5,
    'l2_reg': 1e-5,
    'margin': 0.1,
    'epochs': 500,
    'patience': 20,     
    'min_delta': 1e-4
}

# Dictionnaire qui mappe chaque type de relation à un identifiant numérique
RELATION_MAP = {
    "Adjacence": 0,
    "Dérivation": 1,
    "Continuation": 2,
    "Scission": 3,
    "Fusion": 4
}

# Liste des noms des attributs continus utilisés pour la normalisation ou l'extraction de features
NUM_CONT = ['Aire','Perimeter','Mean','std','variance','Hauteur','Largeur']

# Dictionnaire qui associe chaque date (clé) à un indice (valeur) pour l'encodage temporel
DATA_TO_IDX = {
    "2015/01":0, "2015/05":1, "2016/05":2, "2016/11":3,
    "2017/03":4, "2017/11":5, "2018/11":6, "2019/03":7,
    "2020/03":8, "2020/11":9, "2021/03":10, "2021/11":11,
    "2022/06":12, "2023/09":13, "2024/01":14, "2025/02":15
}

# Nombre de couches dans mon modèle MGCN
N_LAYERS = 8
# Taux de dropout utilisé dans le modèle
DROPOUT = 0.3
# Nombre de types de relations dans le graphe
NUM_RELATION = 5


MOTIFS_DATA_PATH_1 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=50_s=1_500_pairs_4_k-hop_32.json"
MOTIFS_DATA_PATH_2 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=1000_s=2_500_pairs_4_k-hop_32.json"

MOTIFS_DATA_PATH_3 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=100_s=1_500_pairs_4_k-hop_64.json"
MOTIFS_DATA_PATH_4 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=100_s=2_500_pairs_4_k-hop_64.json"

MOTIFS_DATA_PATH_5 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=6_N=100_s=1_500_pairs_6_k-hop_32.json"
MOTIFS_DATA_PATH_6 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=6_N=100_s=2_500_pairs_6_k-hop_32.json"

MOTIFS_DATA_PATH_7 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=6_N=100_s=1_500_pairs_6_k-hop_64.json"
MOTIFS_DATA_PATH_8 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=6_N=100_s=2_500_pairs_6_k-hop_64.json"

MOTIFS_DATA_PATH_9 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=8_N=1000_s=2_500_pairs_8_k-hop_32.json"
MOTIFS_DATA_PATH_10 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=6_N=100_s=2_500_pairs_8_k-hop_32.json"

# MOTIFS_DATA_PATH_6 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=200_s=1_500_pairs_10_k-hop_16.json"
# MOTIFS_DATA_PATH_7 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=200_s=1_500_pairs_4_k-hop_32.json"
# MOTIFS_DATA_PATH_8 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=200_s=1_500_pairs_4_k-hop_32.json"
# MOTIFS_DATA_PATH_9 = "/home/rida/GNN/Search_phase/Motifs_data/Motifs_k=4_N=200_s=1_500_pairs_4_k-hop_32.json"

VIS_LOSS_TRAIN_VAL_500_4 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_500_4_32.png"
VIS_LOSS_TRAIN_VAL_500_6 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_1000_6_16.png"
VIS_LOSS_TRAIN_VAL_500_8 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_1000_8_16.png"
VIS_LOSS_TRAIN_VAL_500_5 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_2000_5_16.png"
VIS_LOSS_TRAIN_VAL_500_10 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_500_10_16.png"

VIS_LOSS_TRAIN_VAL_500_12 = "/home/rida/GNN/Embedding_phase/Visualisation/VIS_LOSS_TRAIN_VAL_300_12_16.png"
