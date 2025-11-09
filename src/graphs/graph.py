from typing import Dict, Set, List, Tuple
from dataclasses import dataclass

@dataclass
class GraphMetrics:
    ordem: int
    tamanho: int
    densidade: float

    def to_dict(self) -> dict:
        return {
            "ordem": self.ordem,
            "tamanho": self.tamanho,
            "densidade": self.densidade,
        }

class Graph:
    def __init__(self):
        self.adjacencies: Dict[str, Set[str]] = {}
        self.weights: Dict[Tuple[str, str], float] = {}

    def add_node(self, node: str) -> None:
        if node not in self.adjacencies:
            self.adjacencies[node] = set()

    def add_edge(self, first_node: str, second_node: str, weight: float = 1.0) -> None:
        self.add_node(first_node)
        self.add_node(second_node)

        self.adjacencies[first_node].add(second_node)
        self.weights[(first_node, second_node)] = weight

        self.adjacencies[second_node].add(first_node)
        self.weights[(second_node, first_node)] = weight

    def get_neighbors(self, node: str) -> Set[str]:
        return self.adjacencies.get(node, set())

    def get_vertices(self) -> List[str]:
        return list(self.adjacencies.keys())

    def get_degree(self, node: str) -> int:
        return len(self.adjacencies.get(node, set()))

    def get_order(self) -> int:
        return len(self.adjacencies)

    def get_size(self) -> int:
        return sum(len(neighbors) for neighbors in self.adjacencies.values()) // 2

    def get_density(self) -> float:
        order = self.get_order()

        if order < 2:
            return 0.0

        size = self.get_size()

        max_edges = order * (order - 1) / 2

        if max_edges > 0:
            return size / max_edges

        return 0.0

    def get_metrics(self) -> GraphMetrics:
        return GraphMetrics(
            ordem=self.get_order(),
            tamanho=self.get_size(),
            densidade=self.get_density(),
        )

    def get_subgraph(self, vertices: Set[str]):
        subgraph = Graph()

        for node in vertices:
            if node in self.adjacencies:
                subgraph.add_node(node)

        for u in vertices:
            if u not in self.adjacencies:
                continue

            for v in self.adjacencies[u]:
                if v in vertices:
                    if u <= v:
                        weight = self.weights.get((u, v), 1.0)
                        subgraph.add_edge(u, v, weight)

        return subgraph

    def has_node(self, node: str) -> bool:
        return node in self.adjacencies

    def has_edge(self, first_node: str, second_node: str) -> bool:
        return (
            first_node in self.adjacencies
            and second_node in self.adjacencies[first_node]
        )

    def get_weight(self, first_node: str, second_node: str) -> float:
        return self.weights.get((first_node, second_node), float("inf"))

    def get_ego_network(self, node: str):
        if node not in self.adjacencies:
            return Graph()

        ego_vertices = {node} | self.get_neighbors(node)

        return self.get_subgraph(ego_vertices)
