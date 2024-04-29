def read_dimacs(filename):
    vertices = {}
    arcs = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()

            if parts[0] == 'p':
                num_vertices = int(parts[2])
                num_arcs = int(parts[3])
            elif parts[0] == 'n':
                vertex = int(parts[1])
                cost = int(parts[2])
                vertices[vertex] = {'cost': cost}
            elif parts[0] == 'a':
                source = int(parts[1])
                dest = int(parts[2])
                cost = int(parts[3])
                capacity = int(parts[4])
                headway = int(parts[5])
                arcs.append((source, dest, cost, capacity, headway))

    return num_vertices, num_arcs, vertices, arcs

def calculate_time_windows(vertices, arcs):
    time_windows = {}

    for source, dest, cost, _, _ in arcs:
        if dest not in vertices:
            vertices[dest] = {'cost': 0}  # Assume default cost is 0 for newly encountered vertices
        if dest not in time_windows:
            time_windows[dest] = [vertices[dest]['cost'], vertices[dest]['cost']]
        time_windows[dest][0] = min(time_windows[dest][0], vertices[source]['cost'])
        time_windows[dest][1] = max(time_windows[dest][1], vertices[source]['cost'] + cost)

    return time_windows

def main():
    filename = 'simpleInput2.txt'
    num_vertices, num_arcs, vertices, arcs = read_dimacs(filename)
    time_windows = calculate_time_windows(vertices, arcs)

    print("Time Windows:")
    for vertex, tw in time_windows.items():
        print(f"Vertex {vertex}: {tw[0]} - {tw[1]}")

if __name__ == "__main__":
    main()
