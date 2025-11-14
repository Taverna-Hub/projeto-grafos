import sys
from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from graphs.algorithms import Algorithms
from graphs.graph import Graph


def load_bitcoin_graph(file_path: str, max_nodes: int = None):
    graph_dict = {}
    graph_obj = Graph()
    edges_data = []
    nodes_seen = set()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            if len(row) < 3:
                continue

            source, target, rating = row[0], row[1], float(row[2])

            if max_nodes:
                if source not in nodes_seen and len(nodes_seen) >= max_nodes:
                    continue
                if target not in nodes_seen and len(nodes_seen) >= max_nodes:
                    continue
                nodes_seen.add(source)
                nodes_seen.add(target)

            if source not in graph_dict:
                graph_dict[source] = []
            if target not in graph_dict:
                graph_dict[target] = []

            graph_dict[source].append((target, rating))

            graph_obj.add_node(source)
            graph_obj.add_node(target)
            graph_obj.add_edge(source, target, rating)

            edges_data.append((source, target, rating))

    return graph_dict, graph_obj, edges_data


def spring_layout(nodes: list, edges: list, iterations: int = 50, k: float = 0.5):
    random.seed(42)
    pos = {node: (random.uniform(0, 1), random.uniform(0, 1)) for node in nodes}

    area = 1.0
    k_sq = k * k
    temp = 0.1

    for iteration in range(iterations):
        displacement = {node: np.array([0.0, 0.0]) for node in nodes}

        for i, v in enumerate(nodes):
            for u in nodes[i + 1 :]:
                delta = np.array(pos[v]) - np.array(pos[u])
                dist = np.linalg.norm(delta)
                if dist > 0:
                    force = k_sq / dist
                    displacement[v] += (delta / dist) * force
                    displacement[u] -= (delta / dist) * force

        for source, target in edges:
            delta = np.array(pos[target]) - np.array(pos[source])
            dist = np.linalg.norm(delta)
            if dist > 0:
                force = dist * dist / k
                displacement[source] += (delta / dist) * force
                displacement[target] -= (delta / dist) * force

        for node in nodes:
            disp = displacement[node]
            disp_norm = np.linalg.norm(disp)
            if disp_norm > 0:
                pos[node] = tuple(
                    np.array(pos[node]) + (disp / disp_norm) * min(disp_norm, temp)
                )

        temp *= 0.95

    return pos


def visualize_graph_sample(
    edges_data: list,
    max_nodes: int = 50,
    output_path: str = "bitcoin_graph_sample.png",
):

    nodes_to_include = set()
    filtered_edges = []

    for source, target, weight in edges_data:
        if len(nodes_to_include) < max_nodes:
            nodes_to_include.add(source)
            nodes_to_include.add(target)

        if source in nodes_to_include and target in nodes_to_include:
            filtered_edges.append((source, target, weight))

        if len(nodes_to_include) >= max_nodes:
            break

    nodes_list = list(nodes_to_include)
    edges_for_layout = [(s, t) for s, t, _ in filtered_edges]

    pos = spring_layout(nodes_list, edges_for_layout, iterations=30, k=0.3)

    fig, ax = plt.subplots(figsize=(14, 10))

    weights = [w for _, _, w in filtered_edges]
    if weights:
        min_w, max_w = min(weights), max(weights)
        norm_weights = [(w - min_w) / (max_w - min_w + 0.001) for w in weights]
    else:
        norm_weights = []

    for (source, target, weight), norm_w in zip(filtered_edges, norm_weights):
        x_vals = [pos[source][0], pos[target][0]]
        y_vals = [pos[source][1], pos[target][1]]

        color = plt.cm.RdYlGn(norm_w)
        ax.plot(x_vals, y_vals, "-", color=color, alpha=0.4, linewidth=1.5, zorder=1)

        dx = x_vals[1] - x_vals[0]
        dy = y_vals[1] - y_vals[0]
        ax.arrow(
            x_vals[0] + dx * 0.5,
            y_vals[0] + dy * 0.5,
            dx * 0.001,
            dy * 0.001,
            head_width=0.02,
            head_length=0.01,
            fc=color,
            ec=color,
            alpha=0.6,
            zorder=2,
        )

    for node in nodes_list:
        x, y = pos[node]
        ax.scatter(
            x,
            y,
            s=300,
            c="lightblue",
            alpha=0.7,
            edgecolors="steelblue",
            linewidths=1.5,
            zorder=3,
        )

        if len(nodes_list) <= 30:
            ax.text(x, y, node, fontsize=7, ha="center", va="center", zorder=4)

    ax.set_title(
        f"Grafo Bitcoin Alpha - Amostra ({len(nodes_list)} nós, {len(filtered_edges)} arestas)",
        fontsize=14,
        fontweight="bold",
    )
    ax.axis("off")
    ax.set_aspect("equal")

    if weights:
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.RdYlGn, norm=plt.Normalize(vmin=min_w, vmax=max_w)
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Rating (Confiança)", rotation=270, labelpad=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def visualize_degree_distribution(
    graph_obj: Graph, output_path: str = "bitcoin_degree_distribution.png"
):
    degrees = [graph_obj.get_degree(node) for node in graph_obj.get_vertices()]
    degree_counter = Counter(degrees)

    avg_degree = np.mean(degrees)
    median_degree = np.median(degrees)

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    ax1.hist(degrees, bins=50, color="steelblue", alpha=0.7, edgecolor="black")
    ax1.axvline(
        avg_degree,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Média: {avg_degree:.2f}",
    )
    ax1.axvline(
        median_degree,
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Mediana: {median_degree:.2f}",
    )
    ax1.set_xlabel("Grau", fontsize=12)
    ax1.set_ylabel("Frequência", fontsize=12)
    ax1.set_title("Distribuição de Graus - Histograma", fontsize=14, fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    sorted_degrees = sorted(degree_counter.items())
    degrees_x = [d for d, _ in sorted_degrees]
    counts_y = [c for _, c in sorted_degrees]

    ax2.loglog(degrees_x, counts_y, "o-", color="darkgreen", markersize=6, alpha=0.7)
    ax2.set_xlabel("Grau (log)", fontsize=12)
    ax2.set_ylabel("Frequência (log)", fontsize=12)
    ax2.set_title(
        "Distribuição de Graus - Escala Log-Log", fontsize=14, fontweight="bold"
    )
    ax2.grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def visualize_distance_heatmap(
    graph_dict: dict,
    sample_size: int = 30,
    output_path: str = "../../out/bitcoin_distance_heatmap.png",
):

    algo = Algorithms(graph_dict)

    nodes = list(graph_dict.keys())
    node_degrees = [(node, len(graph_dict[node])) for node in nodes]
    node_degrees.sort(key=lambda x: x[1], reverse=True)
    sample_nodes = [node for node, _ in node_degrees[:sample_size]]

    n = len(sample_nodes)
    distance_matrix = np.full((n, n), np.inf)

    for i, source in enumerate(sample_nodes):
        for j, target in enumerate(sample_nodes):
            if i == j:
                distance_matrix[i][j] = 0
            else:
                level, _ = algo.bfs(source, target, graph_dict)
                if level != -1:
                    distance_matrix[i][j] = level

    max_finite = np.max(distance_matrix[distance_matrix != np.inf])
    distance_matrix[distance_matrix == np.inf] = max_finite + 1

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(distance_matrix, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(sample_nodes, rotation=90, fontsize=7)
    ax.set_yticklabels(sample_nodes, fontsize=7)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Distância (número de arestas)", rotation=270, labelpad=20)

    ax.set_title(
        f"Heatmap de Distâncias - Bitcoin Alpha\n({sample_size} nós mais conectados)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    finite_distances = distance_matrix[distance_matrix <= max_finite]


def main():
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data" / "bitcoin_alpha.csv"
    output_dir = project_root / "out" / "second_part"

    output_dir.mkdir(parents=True, exist_ok=True)

    graph_dict, graph_obj, edges_data = load_bitcoin_graph(str(data_path))

    visualize_degree_distribution(
        graph_obj, output_path=str(output_dir / "bitcoin_degree_distribution.png")
    )


if __name__ == "__main__":
    main()
