import sys
import time
import tracemalloc
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms


def test_dijkstra_bitcoin_alpha():
    csv_path = Path(__file__).parent.parent / "data" / "bitcoin_alpha_no_negative.csv"
    algo = Algorithms()
    graph = algo.load_graph_from_csv(str(csv_path))

    all_nodes = list(graph.keys())
    pairs = [
        (all_nodes[0], all_nodes[10]),
        (all_nodes[50], all_nodes[100]),
        (all_nodes[200], all_nodes[300]),
        (all_nodes[500], all_nodes[600]),
        (all_nodes[1000], all_nodes[1500]),
    ]

    results = []

    for i, (origin, destination) in enumerate(pairs, 1):

        tracemalloc.start()
        start_time = time.perf_counter()

        weight, path = algo.dijkstra(origin, destination, graph)

        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time

        path_nodes = path.split(" -> ") if path != "No path found" else []
        path_length = len(path_nodes)

        results.append(
            {
                "origin": origin,
                "destination": destination,
                "weight": weight,
                "path_length": path_length,
                "time_seconds": elapsed_time,
                "peak_memory_mb": peak / 1024 / 1024,
                "found": weight != float("inf"),
            }
        )

    return results


if __name__ == "__main__":
    test_dijkstra_bitcoin_alpha()
