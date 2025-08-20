import torch
import random
from collections import defaultdict
from typing import Dict, Tuple
import json
from typing import Dict, Set, Tuple, List
from torch_geometric.utils.convert import from_networkx
from datetime import datetime
import networkx as nx

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def margin(cand_emb, curr_emb):
    delta = torch.clamp(cand_emb - curr_emb, min=0)
    score = float((delta * delta).sum())
    return score



def prepared_data(GST):

    if GST.number_of_edges() == 0:
        data = from_networkx(GST, group_node_attrs=['x'])
        data.edge_index = torch.empty((2, 0), dtype=torch.long, device=device)
        data.edge_type = torch.empty((0,), dtype=torch.long, device=device)
        data.edge_score = torch.empty((0,), dtype=torch.float, device=device)
    else:
        data = from_networkx(
            GST,
            group_node_attrs=['x'],
            group_edge_attrs=['edge_type', 'edge_score']
        )
        num_edges = data.edge_index.size(1)
        if hasattr(data, 'edge_attr') and data.edge_attr.size(1) >= 2:
            data.edge_type = data.edge_attr[:, 0].long()
            data.edge_score = data.edge_attr[:, 1].float()
        else:
            data.edge_type = torch.zeros(num_edges, dtype=torch.long, device=device)
            data.edge_score = torch.zeros(num_edges, dtype=torch.float, device=device)
    data.x = data.x.float()
    data.batch = torch.zeros(data.num_nodes, dtype=torch.long, device=device)
    return data.to(device)




def search_motifs(GST: nx.Graph, model, K: int, s: int, N: int):
    motifs_count: Dict[Tuple[int, ...], int] = defaultdict(int)
    motifs_bestscore: Dict[Tuple[int, ...], float] = {}
    nodes = list(GST.nodes())

    for k in range(2, K + 1):
        print(f"\n=== Extraction des motifs de taille {k}/{K} ===")
        for _ in range(N):
            v = random.choice(nodes)
            sub_nodes = {v}
            best_score = float('inf')

            while len(sub_nodes) < k:
                G_curr = GST.subgraph(sub_nodes)
                curr_emb = model(prepared_data(G_curr)).to(device)

                neighbors = {nbr for u in sub_nodes for nbr in GST.neighbors(u)}
                candidates = neighbors - sub_nodes
                if not candidates:
                    break

                best_u, best_margin = None, float('inf')
                for u in candidates:
                    cand_nodes = sub_nodes | {u}
                    G_cand = GST.subgraph(cand_nodes)
                    cand_emb = model(prepared_data(G_cand)).to(device)
                    margin_val = margin(cand_emb, curr_emb)
                    if margin_val < best_margin:
                        best_margin, best_u = margin_val, u

                if best_u is None:
                    break

                sub_nodes.add(best_u)
                best_score = best_margin

            key = tuple(sorted(sub_nodes))
            motifs_count[key] += 1
            motifs_bestscore[key] = min(motifs_bestscore.get(key, float('inf')), best_score)

    frequent_motifs_with_scores: List[Tuple[nx.Graph, float]] = []
    for key, count in motifs_count.items():
        if count >= s:
            score_min = motifs_bestscore[key]
            G_sub = GST.subgraph(key).copy()
            frequent_motifs_with_scores.append((G_sub, score_min))

    return frequent_motifs_with_scores


def save_motifs(frequent_motifs,output_path):
   
    output = []
    for idx, (Gs, score) in enumerate(frequent_motifs, start=1):
        motif_list = [{
            "motif_id": idx,
            "sous Graphe": Gs,
            "score": score
        }]

        output.append(motif_list)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Motifs sauvegardés avec IDs dans : {output_path}")




