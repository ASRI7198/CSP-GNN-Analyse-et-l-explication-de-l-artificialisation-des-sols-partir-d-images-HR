
def Adjacence(graphe):
    nodes = list(graphe.nodes())
    n = len(nodes)
    for i in range(n):
        for j in range(i + 1, n):
            poly_i = graphe.nodes[nodes[i]]['geometry']
            poly_j = graphe.nodes[nodes[j]]['geometry']
            if poly_i.touches(poly_j):
                graphe.add_edge(nodes[i], nodes[j], relation='Adjacence')








                

