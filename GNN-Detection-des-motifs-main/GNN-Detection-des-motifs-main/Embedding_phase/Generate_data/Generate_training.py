import random
import torch
from torch_geometric.utils import k_hop_subgraph, subgraph
from torch_geometric.data import Data
from torch_geometric.utils.convert import from_networkx

def build_pyg_data(GST):
    """
    Convertit le graphe NetworkX en Data PyG et renvoie tous les attributs utiles.
    """
    pyg_data = from_networkx(
        GST,
        group_node_attrs=['x'],
        group_edge_attrs=['edge_type', 'edge_score']
    )
    return pyg_data

def get_khop_nodes(edge_index, root, k_hops):
    nodes, _, _, _ = k_hop_subgraph(root, k_hops, edge_index, relabel_nodes=False)
    return set(nodes.tolist())

def sample_positive(data, k_hops):
    edge_index, x, edge_type, edge_score, num_nodes = (data.edge_index, data.x, data.edge_attr[:, 0].cpu().numpy().tolist(), data.edge_attr[:, 0].cpu().numpy().tolist(), data.num_nodes)
    v = random.randrange(num_nodes)
    B_nodes = get_khop_nodes(edge_index, v, k_hops)
    remove_cnt = random.randint(1, len(B_nodes)-1)
    A_nodes = set(random.sample(list(B_nodes), len(B_nodes)-remove_cnt))
    data_A = nodes_to_data(A_nodes, edge_index, x, edge_type, edge_score)
    data_B = nodes_to_data(B_nodes, edge_index, x, edge_type, edge_score)
    return data_A, data_B, 1, B_nodes

def sample_negative(data, k_hops, B_nodes):
    edge_index, x, edge_type, edge_score, num_nodes = (data.edge_index, data.x, data.edge_attr[:, 0].cpu().numpy().tolist(), data.edge_attr[:, 0].cpu().numpy().tolist(), data.num_nodes)
    while True:
        v2 = random.randrange(num_nodes)
        Aneg_nodes = get_khop_nodes(edge_index, v2, k_hops)
        if not Aneg_nodes.issubset(B_nodes):
            data_Aneg = nodes_to_data(Aneg_nodes, edge_index, x, edge_type, edge_score)
            data_B    = nodes_to_data(B_nodes, edge_index, x, edge_type, edge_score)
            return data_Aneg, data_B, -1



def nodes_to_data(node_set, edge_index, x, edge_type, edge_score):
    """
    Construit un Data PyG pour le sous-graphe induit par node_set,
    en gardant edge_type et edge_score alignés avec sub_ei.
    """

    nodes_list = list(node_set)
    mask = torch.tensor(nodes_list, dtype=torch.long)

    sub_ei, _, edge_mask = subgraph(mask,edge_index,relabel_nodes=True,return_edge_mask=True)

    sub_x = x[mask]
    edge_type = torch.tensor(edge_type, dtype=torch.long)
    edge_score = torch.tensor(edge_score, dtype=torch.float)
    sub_edge_type  = edge_type[edge_mask]
    sub_edge_score = edge_score[edge_mask]

    data = Data(x=sub_x, edge_index=sub_ei)
    data.edge_type  = sub_edge_type
    data.edge_score = sub_edge_score
    return data

def generate_training_data_pyg(GST, num_pairs, k_hops=3):
    data = build_pyg_data(GST)
    pairs = []
    for _ in range(num_pairs):
        A_p, B_p, pos_lbl, Bp_nodes = sample_positive(data, k_hops)
        pairs.append((A_p, B_p, pos_lbl))
        print(f"Positive pair sampled: {len(A_p.x)} nodes in A, {len(B_p.x)} nodes in B")
        A_n, B_n, neg_lbl = sample_negative(data, k_hops, Bp_nodes)
        print(f"Negative pair sampled: {len(A_n.x)} nodes in A, {len(B_n.x)} nodes in B")
        pairs.append((A_n, B_n, neg_lbl))
    return pairs


def transform_to_float(Data):
    for A, B, _ in Data:
        A.x          = A.x.float()
        A.edge_type  = A.edge_type.long()
        A.edge_score = A.edge_score.float()
        B.x          = B.x.float()
        B.edge_type  = B.edge_type.long()
        B.edge_score = B.edge_score.float()
    return Data



