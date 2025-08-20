import sys
sys.path.append('/home/rida/GNN')

import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from Embedding_phase.Generate_data.config import RELATION_MAP,NUM_CONT,DATA_TO_IDX


tscaler_cont = StandardScaler()
tscaler_time = StandardScaler()
ohe_classe = OneHotEncoder(sparse_output=False, categories=[np.arange(8)])


def preprocess_node_features(GST):
    """
    Prétraite les attributs nodaux pour le GNN :
    - Log-transform + standardisation pour toutes les variables continues
    - Standardisation pour date (année/mois en indice)
    - One-hot encoding pour Classe (0–7)

    Retourne un np.array [n_nodes, n_features]
    """
    all_nodes = [GST.nodes[n] for n in GST.nodes()]
    Xc, Xt, Xcl = [], [], []

    for d in all_nodes:
        cont_vals = []

        for attr in NUM_CONT:
            val = float(d[attr])
            val = np.log1p(val)
            cont_vals.append(val)
 
        C = d['centroid']
        coords = C.replace("POINT (", "").replace(")", "").split()
        cx, cy = float(coords[0]), float(coords[1])
        cont_vals.extend([np.log1p(abs(cx)) * np.sign(cx), np.log1p(abs(cy)) * np.sign(cy)])
        Xc.append(cont_vals)

        idx = DATA_TO_IDX.get(d['year'])
        Xt.append([idx])
        Xcl.append([int(d['classe'])])


    Xc = tscaler_cont.fit_transform(np.array(Xc, dtype=float))
    Xt = tscaler_time.fit_transform(np.array(Xt, dtype=float))
    Xcl = ohe_classe.fit_transform(np.array(Xcl, dtype=int))
    X_all = np.hstack([Xc, Xt, Xcl])
    return X_all



def Update_attributes(G_ST, node_feature_map):

    for u, _, d in G_ST.edges(data=True):
        d['edge_type'] = RELATION_MAP.get(d.get('relation'))
        d['edge_score'] = float(d.get('Score'))
        del d['relation']
        del d['Score']

    for idx, node in enumerate(G_ST.nodes()):
        features = node_feature_map[idx]
        G_ST.nodes[node]['x'] = features
  
    print("All nodes updated with features.")

    return G_ST
































































