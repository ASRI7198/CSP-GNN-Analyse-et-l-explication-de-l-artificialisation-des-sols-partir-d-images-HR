import torch.nn as nn
import torch.nn.functional as F
import torch_geometric.nn as pyg_nn
from Embedding_phase.Generate_data.config import DROPOUT,N_LAYERS,NUM_RELATION
import torch



class MGCNLayer(nn.Module):
    """
    Couche multigraph respectant la définition GCN :
    - Utilise GCNConv pour chaque type de relation (normalisation + self-loop)
    - Somme les sorties par relation
    - Skip-connection + activation
    """
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.convs = nn.ModuleList([
            pyg_nn.GCNConv(in_dim, out_dim, add_self_loops=True)
            for _ in range(NUM_RELATION)
        ])
   

        self.skip = nn.Linear(in_dim, out_dim, bias=True)
        self.norm = nn.BatchNorm1d(out_dim)
        self.act  = nn.ReLU()

    def forward(self, x, edge_index_list,edge_score_list):
        out = 0
        for conv, edge_index,edge_score in zip(self.convs, edge_index_list,edge_score_list):
            out = out + conv(x, edge_index,edge_score)
        out = out + self.skip(x)
        out = self.norm(out)
        return self.act(out)


class MGCN(nn.Module):
    """
    Multi-Graph GCN :
    - Projection initiale
    - Empilement de couches MGCNLayer
    - Pooling global + MLP de sortie
    """
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()

        self.pre_mp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU()
        )

        self.batch_norm = nn.BatchNorm1d(output_dim, eps=1e-5, momentum=0.1)

        self.layers = nn.ModuleList([
            MGCNLayer(hidden_dim, hidden_dim)
            for _ in range(N_LAYERS)
        ])

        self.post_mp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(hidden_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(32, output_dim)
        )

    def forward(self, data):
        x, batch = data.x, data.batch
        x = self.pre_mp(x)

        types       = data.edge_type
        edge_index  = data.edge_index
        scores = data.edge_score

        edge_index_list = []
        edge_weight_list = []

        for rel in range(NUM_RELATION):
            mask = (types == rel)
            ei_rel = edge_index[:, mask]
            edge_index_list.append(ei_rel)
            ew_rel = scores[mask]
            edge_weight_list.append(ew_rel)
        

        for layer in self.layers:
            x = layer(x, edge_index_list,edge_weight_list)
            x = F.dropout(x, p=DROPOUT)

        x   = pyg_nn.global_add_pool(x, batch)
        out = self.post_mp(x)

        return out
