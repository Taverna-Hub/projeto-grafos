import sys
from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
import random

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from constants import PART2_DIR
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
    adjacency = defaultdict(list)
    for source, target, weight in edges_data:
        adjacency[source].append((target, weight))
        adjacency[target].append((source, weight))

    if not adjacency:
        return

    nodes_by_degree = sorted(
        adjacency.keys(), key=lambda n: len(adjacency[n]), reverse=True
    )
    initial_node = (
        nodes_by_degree[0] if nodes_by_degree else random.choice(list(adjacency.keys()))
    )

    nodes_to_include = set([initial_node])
    frontier = [initial_node]

    while len(nodes_to_include) < max_nodes and frontier:
        current_node = frontier.pop(0)

        for neighbor, _ in adjacency[current_node]:
            if neighbor not in nodes_to_include:
                nodes_to_include.add(neighbor)
                frontier.append(neighbor)

                if len(nodes_to_include) >= max_nodes:
                    break

    filtered_edges = []
    for source, target, weight in edges_data:
        if source in nodes_to_include and target in nodes_to_include:
            filtered_edges.append((source, target, weight))

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

    fig, ax = plt.subplots(figsize=(14, 10))

    ax.hist(degrees, bins=50, color="steelblue", alpha=0.7, edgecolor="black")
    ax.axvline(
        avg_degree,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Média: {avg_degree:.2f}",
    )
    ax.axvline(
        median_degree,
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Mediana: {median_degree:.2f}",
    )
    ax.set_xlabel("Grau", fontsize=12)
    ax.set_ylabel("Frequência", fontsize=12)
    ax.set_title("Distribuição de Graus - Histograma", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def visualize_distance_heatmap(
    graph_dict: dict,
    sample_size: int = 30,
    output_path: str = "bitcoin_distance_heatmap.png",
):

    algo = Algorithms(graph_dict)

    nodes = list(graph_dict.keys())
    node_degrees = [(node, len(graph_dict[node])) for node in nodes]
    node_degrees.sort(key=lambda x: x[1], reverse=True)
    sample_nodes = [node for node, _ in node_degrees[:sample_size]]

    n = len(sample_nodes)
    distance_matrix = np.full((n, n), np.inf)

    for i, source in enumerate(sample_nodes):
        distances, _ = algo.bfs(source, graph_dict)
        for j, target in enumerate(sample_nodes):
            if i == j:
                distance_matrix[i][j] = 0
            elif target in distances:
                distance_matrix[i][j] = distances[target]

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


def create_html_wrapper_part2(
    image_filename: str, title: str, output_path: str, description: str = ""
):

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Bitcoin Alpha Network</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            background-color: #f5f5f5;
        }}
        header {{
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }}
        nav {{
            display: flex;
            justify-content: center;
            gap: 0;
        }}
        .menu-item {{
            position: relative;
        }}
        .menu-item > a {{
            color: white !important;
            text-decoration: none;
            padding: 1rem;
            display: block;
        }}
        .menu-item:hover {{
            background-color: #555;
        }}
        .submenu {{
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            background-color: #444;
            min-width: 250px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
        .menu-item:hover .submenu {{
            display: block;
        }}
        .submenu a {{
            color: white !important;
            text-decoration: none;
            padding: 0.75rem 1rem;
            display: block;
            white-space: nowrap;
        }}
        .submenu a:hover {{
            background-color: #666;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        .description {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
            line-height: 1.6;
        }}
        .image-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="menu-item">
                <a href="#">Grafo dos Bairros do Recife</a>
                <div class="submenu">
                    <a href="../1. Grafo dos Bairros do Recife/1.9 Apresentação interativa do grafo/grafo_interativo.html">Grafo Interativo</a>
                    <a href="../1. Grafo dos Bairros do Recife/1.7 Transforme o percurso em árvore e mostre/arvore_percurso.html">Árvore de Percurso</a>
                    <a href="../1. Grafo dos Bairros do Recife/1.8 Explorações e visualizações analíticas/histograma_distribuicao_graus.html">Histograma de Distribuição de Graus</a>
                    <a href="../1. Grafo dos Bairros do Recife/1.8 Explorações e visualizações analíticas/ranking_densidade_microrregiao.html">Ranking de Densidade por Microrregião</a>
                    <a href="../1. Grafo dos Bairros do Recife/1.8 Explorações e visualizações analíticas/subgrafo_top10_bairros.html">Subgrafo Top 10 Bairros</a>
                </div>
            </div>
            <div class="menu-item">
                <a href="#">Dataset de Histórico de Transações Bitcoin</a>
                <div class="submenu">
                    <a href="bitcoin_degree_distribution.html">Distribuicao de Graus</a>
                    <a href="bitcoin_distance_heatmap.html">Heatmap de Distancias</a>
                    <a href="bitcoin_graph_sample.html">Amostra do Grafo</a>
                    <a href="report.html">Relatorio de Testes</a>
                </div>
            </div>
        </nav>
    </header>

    <div class="container">
        <h1>{title}</h1>
        {f'<p class="description">{description}</p>' if description else ''}
        <div class="image-container">
            <img src="{image_filename}" alt="{title}">
        </div>
    </div>
</body>
</html>"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML wrapper criado: {output_path}")


def main():
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "bitcoin_alpha.csv"
    output_dir = Path(PART2_DIR)

    output_dir.mkdir(parents=True, exist_ok=True)

    graph_dict, graph_obj, edges_data = load_bitcoin_graph(str(data_path))

    visualize_degree_distribution(
        graph_obj, output_path=str(output_dir / "bitcoin_degree_distribution.png")
    )
    create_html_wrapper_part2(
        "bitcoin_degree_distribution.png",
        "Distribuição de Graus - Bitcoin Alpha",
        str(output_dir / "bitcoin_degree_distribution.html"),
        "Análise da distribuição de graus dos nós na rede Bitcoin Alpha. "
        "O histograma mostra a frequência de cada grau.",
    )

    visualize_distance_heatmap(
        graph_dict, output_path=str(output_dir / "bitcoin_distance_heatmap.png")
    )
    create_html_wrapper_part2(
        "bitcoin_distance_heatmap.png",
        "Heatmap de Distâncias - Bitcoin Alpha",
        str(output_dir / "bitcoin_distance_heatmap.html"),
        "Matriz de distâncias (número de arestas) entre os 30 nós mais conectados da rede. "
        "Cores mais quentes indicam distâncias maiores entre os nós.",
    )

    visualize_graph_sample(
        edges_data, output_path=str(output_dir / "bitcoin_graph_sample.png")
    )
    create_html_wrapper_part2(
        "bitcoin_graph_sample.png",
        "Amostra do Grafo - Bitcoin Alpha",
        str(output_dir / "bitcoin_graph_sample.html"),
        "Visualização de uma amostra de 50 nós usando o método Snowball (Bola de Neve). "
        "As cores das arestas representam o rating de confiança entre os usuários.",
    )


if __name__ == "__main__":
    main()
