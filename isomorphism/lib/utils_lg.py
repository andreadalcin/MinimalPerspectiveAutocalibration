import itertools

import networkx as nx
import matplotlib.pyplot as plt


def build_adj(num_points, edges):
    adj = list(map(lambda n: list(map(lambda m: [False, False], range(0, num_points))), range(0, num_points)))
    edges_subsets = list(itertools.combinations((range(0, num_points)), 2))

    for edge in edges:
        edges_subset = edges_subsets[edge % len(edges_subsets)]
        i = edges_subset[0]
        j = edges_subset[1]
        if edge >= len(edges_subsets):
            adj[i][j][1] = True
        else:
            adj[i][j][0] = True

    return adj


def build_labelled_graph(adj, index=0):
    num_pnt = len(adj)
    G = nx.Graph()  # Undirected graph, use DiGraph for directed graph
    # Nodes
    G.add_nodes_from(list(range(num_pnt)))
    # Edges
    for i in range(num_pnt - 1):
        for j in range(i + 1, num_pnt):
            if adj[i][j][0] and adj[i][j][1]:
                G.add_edge(i, j)
            elif adj[i][j][0]:
                G.add_edge(i, j)
            elif adj[i][j][1]:
                G.add_edge(i, j)

    G = nx.line_graph(G)
    attrs = {}
    for node in G.nodes():
        i, j = node
        if adj[i][j][0] and adj[i][j][1]:
            attrs[node] = {"label": "B"}
        elif adj[i][j][0]:
            attrs[node] = {"label": "R"}
        elif adj[i][j][1]:
            attrs[node] = {"label": "G"}

    nx.set_node_attributes(G, attrs)
    # fig, ax = plt.subplots(1, 1)

    # Draw the graph
    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_color="black")
    # Add edge labels
    # edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    # nx.draw(line_graph, ax=ax, with_labels=True, labels={n: d["label"] for n, d in line_graph.nodes(data=True)})
    # ax.set_title(f"Plot: {index}")
    # fig.savefig(f"debug/{index}.png")
    # plt.close(fig)
    # return G, L
    return G, []


# def build_labelled_graph(adj, index=0):
#     num_nodes = len(adj)
#     edges = list(itertools.combinations((range(0, num_nodes)), 2))
#     num_edges = len(edges)
#
#     # Get labels for each edge in the graph
#     L = []
#     for edge in edges:
#         i, j = edge
#         if adj[i][j][0] and adj[i][j][1]:
#             L.append("B")
#         elif adj[i][j][0]:
#             L.append("R")
#         elif adj[i][j][1]:
#             L.append("G")
#         else:
#             L.append("W")
#
#     # Build line-graph
#     G = nx.Graph()  # Undirected graph, use DiGraph for directed graph
#     for edge, label in enumerate(L):
#         G.add_node(edge, label=label)
#
#     for i in range(num_edges - 1):
#         for j in range(i + 1, num_edges):
#             G.add_edge(i, j)
#
#     for edge, label in enumerate(L):
#         if label == "W":
#             G.remove_node(edge)
#
#     # G.remove_node() when label of edge is white?
#     # for edge, label in enumerate(L):
#     #     if label == "W":
#     #         G.remove_node(edge)
#     #
#     # L = list(filter(lambda label: label != "W", L))
#
#     # fig, ax = plt.subplots(1, 1)
#     # nx.draw(G, ax=ax, with_labels=True, labels={n: d["label"] for n, d in G.nodes(data=True)})
#     # ax.set_title(f"Plot: {index}")
#     # fig.savefig(f"debug/{index}.png")
#     # plt.close(fig)
#     # return G, L
#
#     return G, L


def constr2labels(constr_list, num_points, asym=False, index=0):
    subsets = list(itertools.combinations((range(0, num_points)), 2))
    adj = list(map(lambda n: list(map(lambda m: [False, False], range(0, num_points))), range(0, num_points)))

    # Adjacency Tensor [num_points x num_points x 2]
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
    return build_labelled_graph(adj, index=index)


def is_isomorphic(G1, L1, G2, L2):
    assert len(L1) == len(L2)
    return nx.vf2pp_is_isomorphic(G1, G2, "label")
    # nx.set_node_attributes(G1, dict(zip(G1, L1)), "label")
    # nx.set_node_attributes(G2, dict(zip(G2, L2)), "label")
    # return nx.vf2pp_is_isomorphic(G1, G2, "label")
