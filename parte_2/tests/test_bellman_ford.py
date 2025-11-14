import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms


def create_graph_with_negative_weights() -> Dict[str, List[Tuple[str, float]]]:

    return {
        "A": [("B", 4.0), ("C", 2.0)],
        "B": [("A", 4.0), ("C", -3.0), ("D", 2.0)],
        "C": [("A", 2.0), ("B", -3.0), ("D", 4.0)],
        "D": [("B", 2.0), ("C", 4.0), ("E", 1.0)],
        "E": [("D", 1.0)],
    }


def create_graph_with_negative_cycle() -> Dict[str, List[Tuple[str, float]]]:

    return {
        "A": [("B", 1.0)],
        "B": [("A", 1.0), ("C", -2.0)],
        "C": [("B", -2.0), ("A", -1.0)],
        "D": [("A", 5.0)],
    }


def bellman_ford_with_cycle_detection(start: str, graph: Dict[str, List[Tuple[str, float]]]) -> Tuple[Dict[str, float], bool]:

    if start not in graph:
        return {}, False
    
    distances = {node: float("inf") for node in graph}
    distances[start] = 0.0
    
    num_nodes = len(graph)
    for _ in range(num_nodes - 1):
        for node in graph:
            if distances[node] != float("inf"):
                for neighbor, weight in graph[node]:
                    if distances[node] + weight < distances[neighbor]:
                        distances[neighbor] = distances[node] + weight
    
    has_negative_cycle = False
    for node in graph:
        if distances[node] != float("inf"):
            for neighbor, weight in graph[node]:
                if distances[node] + weight < distances[neighbor]:
                    has_negative_cycle = True
                    break
        if has_negative_cycle:
            break
    
    return distances, has_negative_cycle


def test_bellman_ford_bitcoin_alpha():

    csv_path = Path(__file__).parent.parent.parent / "data" / "bitcoin_alpha.csv"
    algo = Algorithms()
    graph_positive = algo.load_graph_from_csv(str(csv_path))
    
    all_nodes = list(graph_positive.keys())
    source = all_nodes[0]
    
    tracemalloc.start()
    start_time = time.perf_counter()
    
    distances = algo.bellman_ford(source, graph_positive)
    
    end_time = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_time = end_time - start_time
    reachable = len([d for d in distances.values() if d != float('inf')])
    
    result_1 = {
        "test": "positive_weights",
        "source": source,
        "total_nodes": len(graph_positive),
        "reachable_nodes": reachable,
        "time_seconds": elapsed_time,
        "peak_memory_mb": peak / 1024 / 1024,
        "negative_cycle": False
    }
    

    graph_negative = create_graph_with_negative_weights()

    tracemalloc.start()
    start_time = time.perf_counter()
    
    _, has_cycle = bellman_ford_with_cycle_detection("A", graph_negative)
    
    end_time = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_time = end_time - start_time
    
    result_2 = {
        "test": "negative_weights_no_cycle",
        "source": "A",
        "total_nodes": len(graph_negative),
        "negative_cycle": has_cycle,
        "time_seconds": elapsed_time,
        "peak_memory_kb": peak / 1024
    }
    
    
    graph_cycle = create_graph_with_negative_cycle()
    tracemalloc.start()
    start_time = time.perf_counter()
    
    _, has_cycle = bellman_ford_with_cycle_detection("A", graph_cycle)
    
    end_time = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_time = end_time - start_time

    result_3 = {
        "test": "negative_cycle",
        "source": "A",
        "total_nodes": len(graph_cycle),
        "negative_cycle": has_cycle,
        "time_seconds": elapsed_time,
        "peak_memory_kb": peak / 1024
    }
    

    results = [result_1, result_2, result_3]

    return results


if __name__ == "__main__":
    test_bellman_ford_bitcoin_alpha()
