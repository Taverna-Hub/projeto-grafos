import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms



def test_dfs_bitcoin_alpha():
    algo = Algorithms()
    csv_path = Path(__file__).parent.parent / "data" / "bitcoin_alpha.csv"

    algo = Algorithms()
    graph = algo.load_graph_from_csv(str(csv_path))

    all_nodes = list(graph.keys())
    sources = [all_nodes[0], all_nodes[100], all_nodes[500]]

    results = []

    for i, source in enumerate(sources, 1):
        tracemalloc.start()
        start_time = time.perf_counter()

        visit_order, back_edges, has_cycles = algo.dfs(source, graph)

        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time

        results.append(
            {
                "source": source,
                "visited_nodes": len(visit_order),
                "total_nodes": len(graph),
                "has_cycles": has_cycles,
                "back_edges": len(back_edges),
                "time_seconds": elapsed_time,
                "peak_memory_mb": peak / 1024 / 1024,
            }
        )

    return results


if __name__ == "__main__":
    test_dfs_bitcoin_alpha()
