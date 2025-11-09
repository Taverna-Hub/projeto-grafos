import csv
import json
import heapq
from pathlib import Path
from collections import deque
from typing import Dict, List, Tuple, Optional, Set

from constants import ADJACENCIES_PATH, ENDERECOS_PATH, DISTANCIAS_ENDERECOS_PATH, PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH

class Algorithms:

    def __init__(self, graph: Optional[Dict[str, List[Tuple[str, float]]]] = None):
        self.graph = graph or {}
    
    def load_graph_from_csv(self, file_path: str) -> Dict[str, List[Tuple[str, float]]]:
        graph = {}
        with open(file_path, "r", encoding="utf-8") as file:
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
        
        self.graph = graph
        return graph

    def dijkstra(self, start: str, end: str, graph: Optional[Dict[str, List[Tuple[str, float]]]] = None) -> Tuple[float, str]:
        graph = graph or self.graph
        if not graph:
            return float("inf"), "Grafo não carregado"
        
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

        return float("inf"), "No path found"
    
    def bfs(self, start: str, end: str, graph: Optional[Dict[str, List[Tuple[str, float]]]] = None) -> Tuple[int, str]:
        pass
    
    def dfs(self, start: str, end: str, graph: Optional[Dict[str, List[Tuple[str, float]]]] = None) -> Tuple[bool, str]:
        pass
    
    def bellman_ford(self, start: str, graph: Optional[Dict[str, List[Tuple[str, float]]]] = None) -> Dict[str, float]:
        pass
    
    def compute_distances_batch(self, addresses_path: str = ENDERECOS_PATH, output_path: str = DISTANCIAS_ENDERECOS_PATH) -> None:
        if not self.graph:
            raise ValueError("Grafo não foi carregado. Execute load_graph_from_csv() primeiro.")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(addresses_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  
            
            with open(output_path, "w", newline='', encoding="utf-8") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"])
                
                count = 0
                for row in reader:
                    x, y, bairro_x, bairro_y = row
                    weight, path = self.dijkstra(bairro_x, bairro_y)
                    writer.writerow([x, y, bairro_x, bairro_y, weight, path])
                    count += 1

                    if bairro_x == "Nova Descoberta" and bairro_y == "Boa Viagem":
                        Path(PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH).parent.mkdir(parents=True, exist_ok=True)
                        with open(PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH, "w", encoding="utf-8") as f:
                            json.dump({
                                "origem": bairro_x,
                                "destino": bairro_y,
                                "custo": weight,
                                "caminho": path
                            }, f, indent=2, ensure_ascii=False)
                        print(f"✓ Caminho Nova Descoberta → Boa Viagem salvo em {PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH}")
                    
                    if count % 10 == 0:
                        print(f"  Processados {count} pares de endereços...")
        
        print(f"✓ Distâncias salvas em {output_path}")

def main():

    print("Carregando grafo...")
    path_finder = Algorithms()
    path_finder.load_graph_from_csv(ADJACENCIES_PATH)
    
    print("Calculando distâncias...")
    path_finder.compute_distances_batch()
    print("✓ Processamento completo!")

if __name__ == "__main__":
    main()
