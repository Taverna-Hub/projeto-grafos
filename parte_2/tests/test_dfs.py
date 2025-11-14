import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms


def dfs_with_cycle_detection(start: str, graph: Dict[str, List[Tuple[str, float]]]) -> Tuple[List[str], List[Tuple[str, str]], bool]:

    if start not in graph:
        return [], [], False
    
    visited = set()
    visit_order = []
    back_edges = []
    rec_stack = set()
    
    def dfs_visit(node: str, parent: Optional[str] = None):
        visited.add(node)
        rec_stack.add(node)
        visit_order.append(node)
        
        for neighbor, _ in graph.get(node, []):
            if neighbor not in visited:
                dfs_visit(neighbor, node)
            elif neighbor in rec_stack and neighbor != parent:
                back_edges.append((node, neighbor))
        
        rec_stack.remove(node)
    
    dfs_visit(start)
    has_cycles = len(back_edges) > 0
    
    return visit_order, back_edges, has_cycles


def test_dfs_bitcoin_alpha():
    csv_path = Path(__file__).parent.parent.parent / "data" / "bitcoin_alpha.csv"
    
    algo = Algorithms()
    graph = algo.load_graph_from_csv(str(csv_path))
    
    all_nodes = list(graph.keys())
    sources = [all_nodes[0], all_nodes[100], all_nodes[500]]
    
    results = []
    
    for i, source in enumerate(sources, 1):
        tracemalloc.start()
        start_time = time.perf_counter()
        
        visit_order, back_edges, has_cycles = dfs_with_cycle_detection(source, graph)
        
        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed_time = end_time - start_time
        
        results.append({
            "source": source,
            "visited_nodes": len(visit_order),
            "total_nodes": len(graph),
            "has_cycles": has_cycles,
            "back_edges": len(back_edges),
            "time_seconds": elapsed_time,
            "peak_memory_mb": peak / 1024 / 1024
        })
 
    return results


if __name__ == "__main__":
    test_dfs_bitcoin_alpha()
