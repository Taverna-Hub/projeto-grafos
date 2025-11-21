import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_bfs import test_bfs_bitcoin_alpha
from test_dfs import test_dfs_bitcoin_alpha
from test_dijkstra import test_dijkstra_bitcoin_alpha
from test_bellman_ford import test_bellman_ford_bitcoin_alpha
from constants import PART2_DIR


def main():

    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset": "bitcoin_alpha.csv",
        "tests": {},
    }

    try:
        bfs_results = test_bfs_bitcoin_alpha()
        report["tests"]["bfs"] = {
            "description": "BFS from ≥3 distinct sources with layer analysis",
            "status": "success",
            "results": bfs_results,
        }
    except Exception as e:
        report["tests"]["bfs"] = {"status": "failed", "error": str(e)}

    try:
        dfs_results = test_dfs_bitcoin_alpha()
        report["tests"]["dfs"] = {
            "description": "DFS from ≥3 distinct sources with cycle detection",
            "status": "success",
            "results": dfs_results,
        }
    except Exception as e:
        report["tests"]["dfs"] = {"status": "failed", "error": str(e)}

    try:
        dijkstra_results = test_dijkstra_bitcoin_alpha()
        report["tests"]["dijkstra"] = {
            "description": "Dijkstra with ≥5 origin-destination pairs (weights ≥ 0)",
            "status": "success",
            "results": dijkstra_results,
        }
    except Exception as e:
        report["tests"]["dijkstra"] = {"status": "failed", "error": str(e)}

    try:
        bellman_results = test_bellman_ford_bitcoin_alpha()
        report["tests"]["bellman_ford"] = {
            "description": "Bellman-Ford with positive, negative weights, and negative cycle",
            "status": "success",
            "results": bellman_results,
        }
    except Exception as e:
        report["tests"]["bellman_ford"] = {"status": "failed", "error": str(e)}

    output_dir = Path(PART2_DIR)
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "report.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


if __name__ == "__main__":
    main()
