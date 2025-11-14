import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.algorithms import Algorithms


class TestBFS:

    def test_bfs_levels_small_graph(self):
        graph = {
            "A": [("B", 1), ("D", 1)],
            "B": [("A", 1), ("C", 1)],
            "C": [("B", 1), ("F", 1)],
            "D": [("A", 1), ("E", 1)],
            "E": [("D", 1), ("F", 1)],
            "F": [("C", 1), ("E", 1)],
        }

        algo = Algorithms(graph)

        level, path = algo.bfs("A", "B")
        assert level == 1, f"Esperado nível 1, mas obteve {level}"
        assert path == "A -> B", f"Caminho incorreto: {path}"

        level, path = algo.bfs("A", "C")
        assert level == 2, f"Esperado nível 2, mas obteve {level}"

        level, path = algo.bfs("A", "F")
        assert level == 3, f"Esperado nível 3, mas obteve {level}"

        level, path = algo.bfs("A", "A")
        assert level == 0, f"Esperado nível 0, mas obteve {level}"
        assert path == "A", f"Caminho incorreto: {path}"

    def test_bfs_no_path(self):
        graph = {"A": [("B", 1)], "B": [("A", 1)], "C": [("D", 1)], "D": [("C", 1)]}

        algo = Algorithms(graph)
        level, path = algo.bfs("A", "C")
        assert level == -1, f"Esperado -1 para caminho inexistente, mas obteve {level}"
        assert path == "No path found", f"Mensagem incorreta: {path}"

    def test_bfs_linear_graph(self):
        graph = {
            "A": [("B", 1)],
            "B": [("A", 1), ("C", 1)],
            "C": [("B", 1), ("D", 1)],
            "D": [("C", 1)],
        }

        algo = Algorithms(graph)

        level, path = algo.bfs("A", "D")
        assert level == 3, f"Esperado nível 3, mas obteve {level}"
        assert path == "A -> B -> C -> D", f"Caminho incorreto: {path}"
