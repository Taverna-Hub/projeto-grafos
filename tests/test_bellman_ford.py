import pytest
import sys
from pathlib import Path
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.algorithms import Algorithms


class TestBellmanFord:

    def test_bellman_ford_positive_weights(self):
        graph = {
            "A": [("B", 4), ("C", 2)],
            "B": [("A", 4), ("D", 3)],
            "C": [("A", 2), ("D", 1)],
            "D": [("B", 3), ("C", 1)],
        }

        algo = Algorithms(graph)
        distances = algo.bellman_ford("A")

        assert distances["A"] == 0.0, f"Distância de A para A deve ser 0"
        assert distances["B"] == 4.0, f"Distância de A para B deve ser 4"
        assert distances["C"] == 2.0, f"Distância de A para C deve ser 2"
        assert distances["D"] == 3.0, f"Distância de A para D deve ser 3"

    def test_bellman_ford_negative_weights_no_cycle(self):
        graph = {"A": [("B", 5), ("C", -2)], "B": [("D", 1)], "C": [("D", 3)], "D": []}

        algo = Algorithms(graph)
        distances = algo.bellman_ford("A")

        assert distances["A"] == 0.0, f"Distância de A para A deve ser 0"
        assert distances["C"] == -2.0, f"Distância de A para C deve ser -2"
        assert (
            distances["D"] == 1.0
        ), f"Distância de A para D deve ser 1 (via C: -2+3=1)"
        assert distances["B"] == 5.0, f"Distância de A para B deve ser 5"

    def test_bellman_ford_negative_weights_complex(self):
        graph = {
            "S": [("A", 5), ("B", 2)],
            "A": [("S", 5), ("C", 1)],
            "B": [("S", 2), ("A", -3), ("C", 4)],
            "C": [("A", 1), ("B", 4)],
        }

        algo = Algorithms(graph)
        distances = algo.bellman_ford("S")

        assert distances["S"] == 0.0, f"Distância de S para S deve ser 0"
        assert distances["B"] == 2.0, f"Distância de S para B deve ser 2"
        assert distances["A"] == -1.0, f"Distância de S para A deve ser -1 (via B)"
        assert distances["C"] == 0.0, f"Distância de S para C deve ser 0 (via A)"

    def test_bellman_ford_negative_cycle_detection(self):
        graph = {
            "A": [("B", 1), ("C", -2)],
            "B": [("A", 1), ("C", -1)],
            "C": [("A", -2), ("B", -1)],
        }

        algo = Algorithms(graph)

        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        distances = algo.bellman_ford("A")

        sys.stdout = old_stdout
        output = captured_output.getvalue()

        assert "Negative cycle detected" in output, "Deve detectar ciclo negativo"

        assert isinstance(distances, dict), "Deve retornar um dicionário"

    def test_bellman_ford_no_negative_cycle_flag(self):
        graph = {"A": [("B", 1)], "B": [("A", 1), ("C", 1)], "C": [("B", 1)]}

        algo = Algorithms(graph)

        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        distances = algo.bellman_ford("A")

        sys.stdout = old_stdout
        output = captured_output.getvalue()

        assert (
            "Negative cycle detected" not in output
        ), "Não deve detectar ciclo negativo"
        assert distances["A"] == 0.0
        assert distances["B"] == 1.0
        assert distances["C"] == 2.0

    def test_bellman_ford_disconnected_graph(self):
        graph = {"A": [("B", 1)], "B": [("A", 1)], "C": [("D", 1)], "D": [("C", 1)]}

        algo = Algorithms(graph)
        distances = algo.bellman_ford("A")

        assert distances["A"] == 0.0
        assert distances["B"] == 1.0
        assert distances["C"] == float(
            "inf"
        ), "Nós desconectados devem ter distância infinita"
        assert distances["D"] == float(
            "inf"
        ), "Nós desconectados devem ter distância infinita"

    def test_bellman_ford_single_node(self):
        graph = {"A": []}

        algo = Algorithms(graph)
        distances = algo.bellman_ford("A")

        assert distances["A"] == 0.0, "Distância do nó para si mesmo deve ser 0"
