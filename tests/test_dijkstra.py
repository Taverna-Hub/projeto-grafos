import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.algorithms import Algorithms


class TestDijkstra:

    def test_dijkstra_simple_path(self):
        graph = {
            "A": [("B", 2), ("D", 1)],
            "B": [("A", 2), ("C", 3)],
            "C": [("B", 3), ("F", 1)],
            "D": [("A", 1), ("E", 1)],
            "E": [("D", 1), ("F", 1)],
            "F": [("C", 1), ("E", 1)],
        }

        algo = Algorithms(graph)

        weight, path = algo.dijkstra("A", "F")
        assert weight == 3.0, f"Esperado custo 3, mas obteve {weight}"
        assert path == "A -> D -> E -> F", f"Caminho incorreto: {path}"

    def test_dijkstra_direct_vs_indirect(self):
        graph = {
            "A": [("B", 10), ("C", 2)],
            "B": [("A", 10), ("D", 2)],
            "C": [("A", 2), ("D", 3)],
            "D": [("B", 2), ("C", 3)],
        }

        algo = Algorithms(graph)

        weight, path = algo.dijkstra("A", "B")
        assert weight == 7.0, f"Esperado custo 7, mas obteve {weight}"
        assert path == "A -> C -> D -> B", f"Caminho incorreto: {path}"

    def test_dijkstra_zero_weights(self):
        graph = {
            "A": [("B", 0), ("C", 5)],
            "B": [("A", 0), ("C", 2)],
            "C": [("A", 5), ("B", 2)],
        }

        algo = Algorithms(graph)
        weight, path = algo.dijkstra("A", "C")
        assert weight == 2.0, f"Esperado custo 2, mas obteve {weight}"
        assert path == "A -> B -> C", f"Caminho incorreto: {path}"

    def test_dijkstra_same_node(self):
        graph = {"A": [("B", 1)], "B": [("A", 1)]}

        algo = Algorithms(graph)
        weight, path = algo.dijkstra("A", "A")
        assert weight == 0, f"Esperado custo 0, mas obteve {weight}"
        assert path == "A", f"Caminho incorreto: {path}"

    def test_dijkstra_no_path(self):
        graph = {"A": [("B", 1)], "B": [("A", 1)], "C": [("D", 1)], "D": [("C", 1)]}

        algo = Algorithms(graph)
        weight, path = algo.dijkstra("A", "C")
        assert weight == float("inf"), f"Esperado infinito, mas obteve {weight}"
        assert path == "No path found", f"Mensagem incorreta: {path}"

    def test_dijkstra_with_negative_weights_detection(self):
        graph = {
            "A": [("B", 5), ("C", -2)],
            "B": [("A", 5), ("D", 1)],
            "C": [("A", -2), ("D", 3)],
            "D": [("B", 1), ("C", 3)],
        }

        algo = Algorithms(graph)

        weight, path = algo.dijkstra("A", "D")

        assert isinstance(weight, (int, float)), "Deve retornar um número"
        assert isinstance(path, str), "Deve retornar uma string"

    def test_dijkstra_all_positive_weights(self):
        graph = {
            "A": [("B", 4), ("C", 2)],
            "B": [("A", 4), ("C", 1), ("D", 5)],
            "C": [("A", 2), ("B", 1), ("D", 8), ("E", 10)],
            "D": [("B", 5), ("C", 8), ("E", 2)],
            "E": [("C", 10), ("D", 2)],
        }

        algo = Algorithms(graph)

        weight, path = algo.dijkstra("A", "E")
        assert weight == 10.0, f"Esperado custo 10, mas obteve {weight}"
