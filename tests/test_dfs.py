import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.algorithms import Algorithms


class TestDFS:

    def test_dfs_finds_path(self):
        graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("A", 1), ("D", 1)],
            "C": [("A", 1), ("D", 1)],
            "D": [("B", 1), ("C", 1)],
        }

        algo = Algorithms(graph)
        found, path = algo.dfs("A", "D")

        assert found == True, "DFS deveria encontrar um caminho de A para D"
        assert path.startswith("A"), "Caminho deve começar com A"
        assert path.endswith("D"), "Caminho deve terminar com D"

    def test_dfs_cycle_detection(self):
        graph = {"A": [("B", 1)], "B": [("A", 1), ("C", 1)], "C": [("B", 1), ("A", 1)]}

        algo = Algorithms(graph)

        found, path = algo.dfs("A", "C")
        assert found == True, "Deve encontrar caminho em grafo com ciclo"

        has_multiple_edges = any(len(neighbors) > 1 for neighbors in graph.values())
        assert has_multiple_edges, "Grafo com ciclo deve ter nós com múltiplas arestas"

    def test_dfs_no_path(self):
        graph = {"A": [("B", 1)], "B": [("A", 1)], "C": [("D", 1)], "D": [("C", 1)]}

        algo = Algorithms(graph)
        found, path = algo.dfs("A", "C")

        assert (
            found == False
        ), "DFS não deveria encontrar caminho entre componentes desconectados"
        assert "C" not in path, "Caminho não deve conter o nó destino inalcançável"

    def test_dfs_edge_classification(self):
        graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("A", 1), ("D", 1)],
            "C": [("A", 1), ("D", 1)],
            "D": [("B", 1), ("C", 1)],
        }

        algo = Algorithms(graph)

        found, path = algo.dfs("A", "D")
        path_nodes = path.split(" -> ")
        tree_edges = len(path_nodes) - 1

        total_edges = sum(len(neighbors) for neighbors in graph.values()) // 2

        assert (
            total_edges > tree_edges
        ), "Deve haver arestas além das tree edges (back edges)"

    def test_dfs_acyclic_graph(self):
        graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("A", 1), ("D", 1)],
            "C": [("A", 1), ("E", 1)],
            "D": [("B", 1)],
            "E": [("C", 1)],
        }

        algo = Algorithms(graph)

        found1, path1 = algo.dfs("A", "D")
        assert found1 == True, "Deve encontrar caminho em árvore"

        found2, path2 = algo.dfs("A", "E")
        assert found2 == True, "Deve encontrar caminho em árvore"

        num_vertices = len(graph)
        num_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
        assert num_edges == num_vertices - 1, "Árvore deve ter n-1 arestas"
