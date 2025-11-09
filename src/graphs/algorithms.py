import csv
import heapq


def load_graph_from_csv(file_path):
    graph = {}
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            source, destination, *_, weight = row
            if weight.strip():
                weight = float(weight)
                if source not in graph:
                    graph[source] = []
                if destination not in graph:
                    graph[destination] = []
                graph[source].append((destination, weight))
                graph[destination].append((source, weight))
    return graph


def dijkstra(graph, start, end):
    priority_queue = [(0, start, [])]
    visited = set()

    while priority_queue:
        current_weight, current_node, path = heapq.heappop(priority_queue)

        if current_node in visited:
            continue

        path = path + [current_node]
        visited.add(current_node)

        if current_node == end:
            return current_weight, " -> ".join(path)

        for neighbor, weight in graph.get(current_node, []):
            if neighbor not in visited:
                heapq.heappush(
                    priority_queue, (current_weight + weight, neighbor, path)
                )

    return (
        float("inf"),
        "No path found",
    )


if __name__ == "__main__":
    file_path = "data/adjacencias_bairros.csv"
    graph = load_graph_from_csv(file_path)
    chosen_nodes = [
        {
            "start_node": "Nova Descoberta",
            "end_node": "Boa Viagem",
        },
        {
            "start_node": "Brejo da Guabiraba",
            "end_node": "Imbiribeira",
        },
        {
            "start_node": "Guabiraba",
            "end_node": "Ibura",
        },
        {
            "start_node": "Linha do Tiro",
            "end_node": "Pina",
        },
        {
            "start_node": "Afogados",
            "end_node": "Macaxeira",
        },
        {
            "start_node": "Várzea",
            "end_node": "Santo Amaro",
        },
        {
            "start_node": "Ponto de Parada",
            "end_node": "Bongi",
        },
    ]

    for entry in chosen_nodes:
        weight, path = dijkstra(graph, entry["start_node"], entry["end_node"])

        print(weight)
        print(path)
        print()
