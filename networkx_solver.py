# using networkx to solve the minimum cost flow problem from a DIMACS file

# import necessary libraries
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

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
        flow_cost = nx.min_cost_flow_cost(G)
        flow_dict = nx.min_cost_flow(G)

        return flow_cost, flow_dict, G

# Print the solution flow and optimal cost with explanation
# Show solution flow cli output format: f"x{supply_node}_{source}_{target}"
def print_solution(flow_cost, flow_dict):
    print(f"Optimal cost: {flow_cost}")
    print("Solution flow:")
    for source, flow in flow_dict.items():
        for target, flow_amount in flow.items():
            if flow_amount > 0:
                print(f"{source} --> {target}: {flow_amount}")

# test
file_path = sys.argv[1]
file_name = file_path.split('/')[-1]
problem_info, node_descriptors, arc_descriptors = read_dimacs_file(file_path)
flow_cost, flow_dict, G = solve_minimum_cost_flow(problem_info, node_descriptors, arc_descriptors)
print(f"Problem: {file_name}")
print(f"Number of nodes: {problem_info['num_nodes']}")
print(f"Number of arcs: {problem_info['num_arcs']}")

print_solution(flow_cost, flow_dict)