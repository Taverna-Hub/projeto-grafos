import sys
import time
import tracemalloc
from pathlib import Path
from collections import deque
from typing import Dict, List, Tuple, Set

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms


def bfs_with_layers(start: str, graph: Dict[str, List[Tuple[str, float]]]) -> Tuple[Dict[str, int], List[Set[str]]]:

    if start not in graph:
        return {}, []
    
    distances = {start: 0}
    layers = [{start}]
    queue = deque([start])
    visited = {start}
    current_layer = 0
    nodes_in_current_layer = 1
    nodes_in_next_layer = 0
    
    while queue:
        node = queue.popleft()
        nodes_in_current_layer -= 1
        
        for neighbor, _ in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = current_layer + 1
                queue.append(neighbor)
                nodes_in_next_layer += 1
        
        if nodes_in_current_layer == 0:
            if nodes_in_next_layer > 0:
                current_layer += 1
                if len(layers) <= current_layer:
                    layers.append(set())

                temp_queue = list(queue)
                layers[current_layer] = set(temp_queue[:nodes_in_next_layer])
                nodes_in_current_layer = nodes_in_next_layer
                nodes_in_next_layer = 0
    
    return distances, layers


def test_bfs_bitcoin_alpha():

    csv_path = Path(__file__).parent.parent.parent / "data" / "bitcoin_alpha.csv"
    
    algo = Algorithms()
    graph = algo.load_graph_from_csv(str(csv_path))
    

    all_nodes = list(graph.keys())
    sources = [all_nodes[0], all_nodes[100], all_nodes[500]]
    
    results = []
    
    for i, source in enumerate(sources, 1):
        
        tracemalloc.start()
        start_time = time.perf_counter()
        
        distances, layers = bfs_with_layers(source, graph)
        
        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed_time = end_time - start_time
        
        reachable = len(distances)
        
        results.append({
            "source": source,
            "reachable_nodes": reachable,
            "total_nodes": len(graph),
            "layers": len(layers),
            "time_seconds": elapsed_time,
            "peak_memory_mb": peak / 1024 / 1024
        })
    
    return results


if __name__ == "__main__":
    test_bfs_bitcoin_alpha()
