import itertools

import networkx as nx


def build_adj(num_points, edges):
    adj = list(map(lambda n: list(map(lambda m: [False, False], range(0, num_points))), range(0, num_points)))
    # edges_num = scipy.special.comb(num_points, 2)
    edges_subsets = list(itertools.combinations((range(0, num_points)), 2))

    for edge in edges:
        edges_subset = edges_subsets[edge % len(edges_subsets)]
        i = edges_subset[0]
        j = edges_subset[1]
        # if not adj[i][j][0] and not adj[i][j][1]:
        #     edges_count += 1
        if edge >= len(edges_subsets):
            adj[i][j][1] = True
            # edges13_count += 1
        else:
            adj[i][j][0] = True
            # edges12_count += 1

    return adj


def build_labelled_graph(adj):
    num_pnt = len(adj)
    G = nx.Graph()  # Undirected graph, use DiGraph for directed graph
    # Nodes
    G.add_nodes_from(list(range(num_pnt)))
    # Edges
    for i in range(num_pnt - 1):
        for j in range(i + 1, num_pnt):
            if adj[i][j][0] or adj[i][j][1]:
                G.add_edge(i, j)

    return G


def constr2labels(constr_list, num_points, asym=False, index=0):
    subsets = list(itertools.combinations((range(0, num_points)), 2))
    adj = list(map(lambda n: list(map(lambda m: [False, False], range(0, num_points))), range(0, num_points)))

    # Adjacency Tensor ( num_points, num_points, 2 )
    for constr in constr_list:
        subset = subsets[constr % len(subsets)]
        n1 = subset[0]  # 1st node
        n2 = subset[1]  # 2nd node

        if constr >= len(subsets):
            # Views 1-3
            adj[n1][n2][1] = True
            adj[n2][n1][1] = True
        else:
            # Views 1-2
            adj[n1][n2][0] = True
            adj[n2][n1][0] = True

    # Graph building
    G = build_labelled_graph(adj)

    # Vertex -> Label mapping
    L = []
    for i in range(num_points):
        tmp = []
        for j in range(num_points):
            if i != j:
                if adj[i][j][0] and adj[i][j][1]:
                    tmp.append("B")
                elif adj[i][j][0]:
                    if asym:
                        tmp.append("G")
                    else:
                        tmp.append("R")
                elif adj[i][j][1]:
                    if asym:
                        tmp.append("R")
                    else:
                        tmp.append("G")

        tmp.sort()
        L.append("".join(tmp))

    return G, L


def is_isomorphic(G1, L1, G2, L2):
    assert len(L1) == len(L2)
    nx.set_node_attributes(G1, dict(zip(G1, L1)), "label")
    nx.set_node_attributes(G2, dict(zip(G2, L2)), "label")
    return nx.vf2pp_is_isomorphic(G1, G2, "label")
