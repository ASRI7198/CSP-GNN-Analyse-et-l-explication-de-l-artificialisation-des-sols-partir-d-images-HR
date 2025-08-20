import pandas as pd
import Noeud as n
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
import Relation_spasital as Rs
from Relation_temporelle import Scission
from Relation_temporelle import Fusion
from Relations_filiation import Continuation
from Relations_filiation import Dérivation
import pandas as pd



def Geometry(path):
    df = pd.read_csv(path)
    multipolygons = df["geometry"].tolist()
    multipolygons = [wkt.loads(geom) for geom in multipolygons]
    return multipolygons

def Classes(path):
    df = pd.read_csv(path)
    classe = df["Classe"].tolist()
    return classe

def DN(path):
    df = pd.read_csv(path)
    dn = df["DN"].tolist()
    return dn

def Area(path):
    df = pd.read_csv(path)
    area = df["Area"].tolist()
    return area

def Perimeter(path):
    df = pd.read_csv(path)
    perimeter = df["perimeter"].tolist()
    return perimeter

def Compacité(path):
    df = pd.read_csv(path)
    compacité = df[" Compacité"].tolist()
    return compacité

def Width(path):
    df = pd.read_csv(path)
    width = df["width"].tolist()
    return width

def Height(path):
    df = pd.read_csv(path)
    height = df["height"].tolist()
    return height

def Rectangularity(path):
    df = pd.read_csv(path)
    rectangularity = df["Rectangularity"].tolist()
    return rectangularity

def mean(path):
    df = pd.read_csv(path)
    mean = df["Mean"].tolist()
    return mean

def std(path):
    df = pd.read_csv(path)
    std = df["Ecart_type"].tolist()
    return std

def variance(path):
    df = pd.read_csv(path)
    variance = df["Variance"].tolist()
    return variance

def Year(path):
    filename = path.split("/")[-1]
    year_parts = filename.replace("Grabels", "").replace(".csv", "").split("_")
    year = f"{year_parts[1]}/{year_parts[2]}"
    return year


def Create_Noeuds(path):
    multipolygons = Geometry(path)
    DN_ = DN(path)
    year = Year(path)
    Area_ = Area(path)
    Perimeter_ = Perimeter(path)
    Compacité_ = Compacité(path)
    Width_ = Width(path)
    Height_ = Height(path)
    Rectangularity_ = Rectangularity(path)
    Classe_ = Classes(path)
    mean_ = mean(path)
    std_ = std(path)
    variance_ = variance(path)

    noeuds = []
    for i in range(len(multipolygons)):
        noeud = n.Noeud(DN_[i],year,Area_[i],Perimeter_[i],Compacité_[i],Width_[i],Height_[i],Rectangularity_[i],mean_[i],std_[i],variance_[i],Classe_[i],multipolygons[i])
        noeuds.append(noeud)
        noeuds[i].compute_all(multipolygons)

    return noeuds

       
def Create_Graph(noeuds):
    G = nx.Graph()
    for i, noeud in enumerate(noeuds):
        G.add_node(i, DN=noeud.DN, year=noeud.year, Aire=noeud.Aire, Perimeter=noeud.Perimeter, 
                Largeur=noeud.Largeur, Hauteur=noeud.Hauteur, Rectangularity=noeud.Rectangularity, 
                Elongation=noeud.Elongation, I_Miller=noeud.I_Miller, classe=noeud.classe,Mean = noeud.mean,
                std=noeud.std, variance=noeud.variance,centroid=noeud.centroid,Nbr_Voisins=noeud.Nbr_Voisins,surface_voisins=noeud.surface_voisins,geometry=noeud.multipolygone)
    
    Rs.Adjacence(G)
    return G

def Create_Graphe_spatio_temporel(G1, G2):
    G_st = nx.MultiDiGraph()

    for n, data in G1.nodes(data=True):
        G_st.add_node((n, data.get('year')), **data)
    for n, data in G2.nodes(data=True):
        G_st.add_node((n, data.get('year')), **data)

    for u, v, data in G1.edges(data=True):
        rela = data.get('relation')
        year_u = G1.nodes[u].get('year')
        year_v = G1.nodes[v].get('year')
        G_st.add_edge((u, year_u), (v, year_v), relation=rela)

    for u, v, data in G2.edges(data=True):
        rela = data.get('relation')
        year_u = G2.nodes[u].get('year')
        year_v = G2.nodes[v].get('year')
        G_st.add_edge((u, year_u), (v, year_v), relation=rela)

    
    print("Scission start")
    G_scission = Scission(G1, G2)
    G_st.add_edges_from(G_scission.edges(data=True))
    print("Scission finich")
    
    print("Fusion start")
    G_fusion = Fusion(G1, G2)
    G_st.add_edges_from(G_fusion.edges(data=True))
    print("Fusion finich")
    

    
    print("Dérivation start")
    G_der = Dérivation(G1,G2)
    G_st.add_edges_from(G_der.edges(data=True))  
    print("Dérivation finich")

    print("Continuation start")
    G_cont = Continuation(G1,G2)
    G_st.add_edges_from(G_cont.edges(data=True))    
    print("Continuation finich")
    

    return G_st


def get_last_year(G):
    years = [data['year'] for _, data in G.nodes(data=True)]
    return max(years)


def get_first_year(G):
    years = [data['year'] for _, data in G.nodes(data=True)]
    return min(years)

def Create_Graphe_spatio_temporel_2(G_st1, G_st2):
    last_year_1 = get_last_year(G_st1)
    first_year_2 = get_first_year(G_st2)

    G1_sub = G_st1.subgraph([n for n, d in G_st1.nodes(data=True) if d['year'] == last_year_1]).copy()
    G2_sub = G_st2.subgraph([n for n, d in G_st2.nodes(data=True) if d['year'] == first_year_2]).copy()
    
    G_cont = Continuation(G1_sub,G2_sub)
    G_der = Dérivation(G1_sub,G2_sub)
    G_scission = Scission(G1_sub, G2_sub)
    G_fusion = Fusion(G1_sub, G2_sub)
    

    G_merged = nx.MultiDiGraph()

    for n, data in G_st1.nodes(data=True):
        G_merged.add_node((n, data.get('year')), **data)
    for n, data in G_st2.nodes(data=True):
        G_merged.add_node((n, data.get('year')), **data)

    
    for u, v, data in G_st1.edges(data=True):
        rela = data.get('relation')
        year_u = G_st1.nodes[u].get('year')
        year_v = G_st1.nodes[v].get('year')
        G_merged.add_edge((u, year_u), (v, year_v), relation=rela)

    for u, v, data in G_st2.edges(data=True):
        rela = data.get('relation')
        year_u = G_st2.nodes[u].get('year')
        year_v = G_st2.nodes[v].get('year')
        G_merged.add_edge((u, year_u), (v, year_v), relation=rela)

    G_merged.add_edges_from(G_cont.edges(data=True))
    G_merged.add_edges_from(G_der.edges(data=True))  
    G_merged.add_edges_from(G_scission.edges(data=True))
    G_merged.add_edges_from(G_fusion.edges(data=True))

    return G_merged


def Stocker_Graph_GraphML(G, name, index):
    keys = [
        ("d0", "DN", "int"),
        ("d1", "year", "string"),
        ("d2", "Aire", "float"),
        ("d3", "Perimeter", "float"),
        ("d4", "Largeur", "float"),
        ("d5", "Hauteur", "float"),
        ("d6", "Rectangularity", "float"),
        ("d7", "Elongation", "float"),
        ("d8", "I_Miller", "float"),
        ("d9", "Mean", "float"),
        ("d10", "std", "float"),
        ("d11", "variance", "float"),
        ("d12", "geometry", "string"),
        ("d13", "centroid", "string"),
        ("d14", "Nbr_Voisins", "int"),
        ("d15", "surface_voisins", "float"),
        ("d16", "classe", "float"),
    ]

    edge_keys = [
        ("e0", "relation", "string"),
        ("e1", "Score", "float"),
    ]

    root = ET.Element("graphml", {
        "xmlns": "http://graphml.graphdrawing.org/xmlns",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
    })

    for kid, name_, typ in keys:
        ET.SubElement(root, "key", attrib={"id": kid, "for": "node", "attr.name": name_, "attr.type": typ})

    for kid, name_, typ in edge_keys:
        ET.SubElement(root, "key", attrib={"id": kid, "for": "edge", "attr.name": name_, "attr.type": typ})

    graph = ET.SubElement(root, "graph", edgedefault="undirected")

    for node, data in G.nodes(data=True):
        if isinstance(node, tuple):
            node_id = f"{node[0]}_{node[1]}"
        else:
            node_id = str(node)
        node_elem = ET.SubElement(graph, "node", id=node_id)
        for kid, name_, typ in keys:
            value = data.get(name_)
            if value is not None:
                ET.SubElement(node_elem, "data", key=kid).text = str(value)

    for i, (u, v, data) in enumerate(G.edges(data=True)):
        u_id = f"{u[0]}_{u[1]}" if isinstance(u, tuple) else str(u)
        v_id = f"{v[0]}_{v[1]}" if isinstance(v, tuple) else str(v)
        edge_elem = ET.SubElement(graph, "edge", source=u_id, target=v_id, id=f"e{i}")
        relation = str(data.get("relation"))
        score = data.get("Score")

        if score is None:
            score = 1.0
        
        ET.SubElement(edge_elem, "data", key="e0").text = relation
        ET.SubElement(edge_elem, "data", key="e1").text = str(score)
   
    tree = ET.ElementTree(root)
    if index == 0:
        path = f"C:/Users/rasri/Desktop/GST/GST/Graphes spatiaux/RS_Grabels{name}.graphml.xml"
    else:
        path = f"/kaggle/working/GST_Grabels{name}.graphml.xml"
    
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"Graphe exporté dans '{path}'")

        
def Read_GraphML(path,name):
    G = nx.read_graphml(path)
    print(f"Graphe spatial '{name}' importé avec succès.")
    print("---------------------------------------------")
    return G


