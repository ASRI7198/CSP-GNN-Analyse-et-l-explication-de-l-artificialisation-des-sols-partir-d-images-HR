import networkx as nx




def afficher_scores_par_relation(G, n=50):
    relations = set(d.get('relation') for _, _, d in G.edges(data=True) if 'relation' in d)
    for rel in relations:
        scores = [d.get('Score') for _, _, d in G.edges(data=True)
                  if d.get('relation') == rel and 'Score' in d]
        print(f"\nRelation : {rel}")
        if scores:
            print("Scores :", scores[:n])
        else:
            print("Aucun score trouvé pour cette relation.")
            

def afficher_years_uniques(G):
    years = set(nx.get_node_attributes(G, 'year').values())
    print("Années (year) disponibles dans le graphe :", sorted(years))


def afficher_statistiques_gst(graphe_gst: nx.MultiDiGraph):
   
    print("--- Statistiques du Graphe Spatio-Temporel ---")
    print(f"Nombre total d'entités (nœuds): {graphe_gst.number_of_nodes()}")
    print(f"Nombre total de relations (arêtes): {graphe_gst.number_of_edges()}")

    types_relations = {}
    for u, v, data in graphe_gst.edges(data=True):
        relation_type = data.get('relation')
        types_relations[relation_type] = types_relations.get(relation_type, 0) + 1

    print("\nRépartition des types de relations:")
    for r_type, count in types_relations.items():
        print(f"  - {r_type}: {count} relations")

    print("\nStatistiques sur les attributs des entités:")

    classes_objets = {}
    for node, data in graphe_gst.nodes(data=True):
        classe = data.get('classe')
        classes_objets[classe] = classes_objets.get(classe, 0) + 1
    if classes_objets:
        print("  - Répartition par 'classe':")
        for classe, count in classes_objets.items():
            print(f"    - {classe}: {count} entités")

    numerical_attributes = ['Aire', 'Perimeter', 'Largeur', 'Hauteur', 'Rectangularity',
                            'Elongation', 'I_Miller', 'Mean', 'std', 'variance',
                            'Nbr_Voisins', 'surface_voisins']

    for attr in numerical_attributes:
        values = [data[attr] for node, data in graphe_gst.nodes(data=True) if attr in data and data[attr] is not None]
        if values:
            try:
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    print(f"  - Attribut '{attr}':")
                    print(f"    - Moyenne: {sum(numeric_values) / len(numeric_values):.2f}")
                    print(f"    - Max: {max(numeric_values):.2f}")
                else:
                    print(f"  - Attribut '{attr}': Aucune valeur numérique valide trouvée.")
            except TypeError:
                print(f"  - Attribut '{attr}': Contient des valeurs non numériques qui empêchent le calcul des statistiques.")
        else:
            print(f"  - Attribut '{attr}': Non trouvé ou aucune valeur pour les entités.")

    years = [data['year'] for node, data in graphe_gst.nodes(data=True) if 'year' in data]
    if years:
        min_year = min(years)
        max_year = max(years)
        print(f"  - Plage d'années des entités: de {min_year} à {max_year}")
    else:
        print("  - Attribut 'year' non trouvé pour les entités.")

    print("\n--- Fin des Statistiques ---")




def afficher_scores_par_relation_par_annee(G):
    """
    Pour chaque relation temporelle ('Fusion', 'Scission')
    et filiation ('Continuation', 'Dérivation'), affiche une ligne par année :
        noeud1_YYYY/MM   relation   noeud2_YYYY/MM   score

    - On utilise G.nodes[u]['year'] au format 'YYYY/MM'.
    - On tronque les labels de nœud de la forme
      "ID_YYYY/MM_YYYY/MM_..." en ne gardant que "ID_YYYY/MM".
    """
    relations_cibles = {'Fusion', 'Scission', 'Continuation', 'Dérivation'}

    def tronquer_label(label: str) -> str:
        parts = label.split('_')
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return label

    for rel in relations_cibles:
        par_annee = {}
        for u, v, data in G.edges(data=True):
            if data.get('relation') != rel or 'Score' not in data:
                continue

            du_str = G.nodes[u].get('year')
            dv_str = G.nodes[v].get('year')
            if not du_str or not dv_str:
                continue

            # on s'attend à 'YYYY/MM'
            try:
                an_u, mois_u = du_str.split('/')
                an_v, mois_v = dv_str.split('/')
                an_u = int(an_u)
                an_v = int(an_v)
            except (ValueError, AttributeError):
                # format inattendu => on skip
                continue

            # on garde une arête par année
            if an_u not in par_annee:
                u_lab = tronquer_label(str(u))
                v_lab = tronquer_label(str(v))
                par_annee[an_u] = (u_lab, du_str, v_lab, dv_str, data['Score'])

        print(f"\nRelation : {rel}")
        if not par_annee:
            print("  Aucun score trouvé pour cette relation.")
        else:
            for annee in sorted(par_annee):
                u_lab, du_str, v_lab, dv_str, score = par_annee[annee]
                print(f"  {u_lab}_{du_str}   {rel}   {v_lab}_{dv_str}   {score}")






