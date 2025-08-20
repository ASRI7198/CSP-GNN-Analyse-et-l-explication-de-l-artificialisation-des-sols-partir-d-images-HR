import networkx as nx
from shapely import wkt
import math

def getDistance(attr1, attr2):
    C1 = attr1.get('centroid')
    C2 = attr2.get('centroid') 
    coords1 = C1.replace("POINT (", "").replace(")", "").split()
    x1, y1 = float(coords1[0]), float(coords1[1])  
    coords2 = C2.replace("POINT (", "").replace(")", "").split()
    x2, y2 = float(coords2[0]), float(coords2[1])
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance



def max_polygon_length(attr):
    geom = attr.get('geometry')
    geom = wkt.loads(geom)
    max_distance = 0
    points = []
    for polygon in geom.geoms:
        points.extend(list(polygon.exterior.coords))
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance > max_distance:
                max_distance = distance
    return max_distance


def Mon_function(attr1, attr2):
    attributs = ['Aire', 'Perimeter', 'Rectangularity', 'I_Miller'] 
    similarities = []
    for attr in attributs:
        v1 = float(attr1.get(attr))
        v2 = float(attr2.get(attr))
        denom = (abs(v1) + abs(v2)) / 2
        sim = 1.0 - abs(v1 - v2) / denom
        similarities.append(sim)
    Score = sum(similarities)/ len(similarities)
    return  Score 



def Scission(G1, G2):
    G_st = Copy_Nodes(G1, G2)
    for n1, attr1 in G1.nodes(data=True):
        matches = []
        seuil_distance = max_polygon_length(attr1)
        for n2, attr2 in G2.nodes(data=True):
            Distance = getDistance(attr1, attr2)
            if Distance <= seuil_distance:
                score = Mon_function(attr1, attr2)
                if score > 0 and score <= 0.9:
                    matches.append(n2)
        if len(matches) > 1:
            aire1 = float(attr1.get('Aire'))
            aire_matches = sum(float(G2.nodes[n2].get('Aire')) for n2 in matches
)
            denom = (abs(aire1) + abs(aire_matches)) / 2
            if abs(aire1 - aire_matches) / denom <= 0.05:
                for n2 in matches:
                    year2 = G2.nodes[n2].get('year')
                    G_st.add_edge((n1, attr1.get('year')), (n2, year2),Score=score ,relation='Scission')
    return G_st



def Fusion(G1, G2):
    G_st = Copy_Nodes(G1, G2)
    for n2, attr2 in G2.nodes(data=True):
        matches = []
        seuil_distance = max_polygon_length(attr2)
        for n1, attr1 in G1.nodes(data=True):
            Distance = getDistance(attr2, attr1)
            if Distance <= seuil_distance:
                score = Mon_function(attr2, attr1)
                if score > 0 and score <= 0.9:
                    matches.append(n1)
        if len(matches) > 1:
            aire2 = float(attr2.get('Aire'))
            aire_matches = sum(float(G1.nodes[n1].get('Aire')) for n1 in matches)
            denom = (abs(aire2) + abs(aire_matches)) / 2
            if abs(aire2 - aire_matches) / denom <= 0.05:
                for n1 in matches:
                    year1 = G1.nodes[n1].get('year')
                    G_st.add_edge((n1, year1), (n2, attr2.get('year')),Score=score ,relation='Fusion')
    return G_st

    
def Copy_Nodes(G1, G2):
    G_st = nx.MultiDiGraph()
    for n in G1.nodes():
        year = G1.nodes[n].get('year')
        G_st.add_node((n, year), **G1.nodes[n])
    for n in G2.nodes():
        year = G2.nodes[n].get('year')
        G_st.add_node((n, year), **G2.nodes[n])
    return G_st



    




