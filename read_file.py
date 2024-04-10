import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Function to read DIMACS file and create a NetworkX graph
def read_dimacs_file(file_name):
    problem_info = {}
    node_descriptors = []
    arc_descriptors = []

    with open(file_name, 'r') as file:
        for line in file:
            if line.startswith('c'):
                # Ignore comment lines
                continue
            elif line.startswith('p'):
                # Parse problem line
                _, problem_type, num_nodes, num_arcs = line.split()
                problem_info['type'] = problem_type
                problem_info['num_nodes'] = int(num_nodes)
                problem_info['num_arcs'] = int(num_arcs)
            elif line.startswith('n'):
                # Parse node descriptor line
                _, node_id, flow = line.split()
                node_descriptors.append((int(node_id), int(flow)))
            elif line.startswith('a'):
                # Parse arc descriptor line
                _, src, dst, low, cap, cost = line.split()
                arc_descriptors.append((int(src), int(dst), int(low), int(cap), int(cost)))
            else:
                # Ignore other lines
                continue

    return problem_info, node_descriptors, arc_descriptors

def solve_minimum_cost_flow(problem_info, node_descriptors, arc_descriptors):

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with supply/demand
    for node_id, flow in node_descriptors:
        if flow > 0:
            G.add_node(node_id, demand=-flow)  # Supply node
        elif flow < 0:
            G.add_node(node_id, demand=-flow)  # Demand node

    # Add arcs with capacity and cost
    for src, dst, _, cap, cost in arc_descriptors:
        G.add_edge(src, dst, capacity=cap, weight=cost)

    # Solve minimum-cost flow problem
    flow_cost, flow_dict = nx.network_simplex(G)

    return flow_cost, flow_dict, G

# Draw the graph show the solution flow, mark the target node with red color, and the source node with green color
# edge which is the solution flow is marked with red color
# edge which is not the solution flow is marked with black color
# edge label will show the flow/capacity/weight/flow cost
# node label will show the demand/supply
# make the graph as verbose as possible
def draw_graph(G, flow_dict):
    pos = nx.spring_layout(G, seed=42)  # Use spring layout with fixed seed for consistent layout

    # Nodes(labels are node names and demand/supply(remove negative sign if supply))
    node_labels = {node: f"Node: {node}\n{'Supply' if G.nodes[node].get('demand', 0) < 0 else 'Demand'}: {abs(G.nodes[node].get('demand', 0))}" for node in G.nodes()}
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos, labels=node_labels)

    # Edges
    for u, v in G.edges():
        if flow_dict[u][v] > 0:
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=2.0, edge_color='red')
        else:
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=1.0, edge_color='black')

    # Mark target node with red color and source node with green color
    target_node = [node for node in G.nodes() if G.nodes[node].get('demand', 0) < 0]
    source_node = [node for node in G.nodes() if G.nodes[node].get('demand', 0) > 0]
    nx.draw_networkx_nodes(G, pos, nodelist=target_node, node_color='green', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=source_node, node_color='red', node_size=500)

    plt.axis('off')

    # Add click event handler
    plt.gcf().canvas.mpl_connect('button_press_event', lambda event: on_click(event, G, flow_dict))

    plt.show()


def on_click(event, G, flow_dict):
    if event.inaxes is None:
        return
    x, y = event.xdata, event.ydata
    node_clicked = None
    edge_clicked = None

    # Check if a node was clicked
    for n, (xx, yy) in nx.spring_layout(G, seed=42).items():
        if (xx - x) ** 2 + (yy - y) ** 2 < 0.01:
            node_clicked = n
            break

    # Check if an edge was clicked
    if not node_clicked:
        for edge in G.edges():
            edge_pos = nx.spring_layout(G, seed=42)[edge[0]], nx.spring_layout(G, seed=42)[edge[1]]
            dist = np.linalg.norm(np.array([edge_pos[0][0] - x, edge_pos[0][1] - y])) + np.linalg.norm(
                np.array([edge_pos[1][0] - x, edge_pos[1][1] - y]))
            if dist < 0.03:
                edge_clicked = edge
                break

    if node_clicked is not None:
        print(f"\nNode: {node_clicked}")
        print(
            f"{'Supply' if G.nodes[node_clicked].get('demand', 0) < 0 else 'Demand'}: {abs(G.nodes[node_clicked].get('demand', 0))}")
        print("Outgoing Flows:")
        for neighbor in G.successors(node_clicked):
            print(f"Flow to {neighbor}: {flow_dict[node_clicked][neighbor]}")
        print("Incoming Flows:")
        for neighbor in G.predecessors(node_clicked):
            print(f"Flow from {neighbor}: {flow_dict[neighbor][node_clicked]}")
    elif edge_clicked is not None:
        print(f"\nEdge: {edge_clicked}")
        print(f"Capacity: {G.edges[edge_clicked]['capacity']}")
        print(f"Weight: {G.edges[edge_clicked]['weight']}")
        print(f"Flow: {flow_dict[edge_clicked[0]][edge_clicked[1]]}")
        print(f"Flow Cost: {flow_dict[edge_clicked[0]][edge_clicked[1]] * G.edges[edge_clicked]['weight']}")
    else:
        print("\nNo node or edge clicked.")



# Run
file_name = 'input.txt'
problem_info, node_descriptors, arc_descriptors = read_dimacs_file(file_name)

# Print problem information, node descriptors, and arc descriptors
print("Problem Information:")
print(problem_info)
print(f"Problem Type: {problem_info['type']}")
print(f"Number of Nodes: {problem_info['num_nodes']}")
print(f"Number of Arcs: {problem_info['num_arcs']}")

print("\nNode Descriptors:")
print(node_descriptors)
for node in node_descriptors:
    print(f"Node: {node[0]} Demand/Supply: {node[1]}")

print("\nArc Descriptors:")
print(arc_descriptors)
for arc in arc_descriptors:
    print(f"Arc: {arc[0]} -> {arc[1]} Lower Bound: {arc[2]} Capacity: {arc[3]} Cost: {arc[4]}")

# Solve minimum cost flow problem
flow_cost, flow_dict, nxGraph = solve_minimum_cost_flow(problem_info, node_descriptors, arc_descriptors)

print("\nMinimum Cost:", flow_cost)
print("Flow:")
for node in flow_dict:
    for neighbor in flow_dict[node]:
        print("From", node, "to", neighbor, "Flow:", flow_dict[node][neighbor])

# print solution flow
print("\nSolution Flow:")
for u, v in nxGraph.edges():
    if flow_dict[u][v] > 0:
        print(f"Flow from {u} to {v}: {flow_dict[u][v]}")
#draw_graph(nxGraph, flow_dict)
print("\nMinimum Cost:", flow_cost)