import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utils.normalize import normalize_name
from pyvis.network import Network
import re

from graphs.graph import Graph
from constants import (
    EGO_BAIRRO_PATH,
    BAIRROS_UNIQUE_PATH,
    PART1_Q8_DIR,
    PART1_Q7_DIR,
    PART1_Q9_DIR,
)


class GraphVisualizer:

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(PART1_Q8_DIR)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        plt.style.use("seaborn-v0_8-darkgrid")
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.titlesize"] = 14
        plt.rcParams["axes.labelsize"] = 12

    def viz_ranking_density_ego_per_microregion(
        self, ego_path: str = EGO_BAIRRO_PATH, bairros_path: str = BAIRROS_UNIQUE_PATH
    ) -> None:

        ego_df = pd.read_csv(ego_path)
        bairros_df = pd.read_csv(bairros_path)

        bairros_df["bairro"] = bairros_df["bairro"].apply(normalize_name)
        ego_df["bairro"] = ego_df["bairro"].apply(normalize_name)

        merged = ego_df.merge(bairros_df, on="bairro", how="left")

        density_by_micro = (
            merged.groupby("microrregiao")
            .agg({"densidade_ego": "mean", "bairro": "count"})
            .reset_index()
        )

        density_by_micro.columns = [
            "microrregiao",
            "densidade_media_ego",
            "num_bairros",
        ]
        density_by_micro = density_by_micro.sort_values(
            "densidade_media_ego", ascending=False
        )

        num_micro = len(density_by_micro)
        fig_height = max(8, num_micro * 0.6)

        fig, ax = plt.subplots(figsize=(14, fig_height))

        y_positions = range(len(density_by_micro))

        bars = ax.barh(
            y_positions,
            density_by_micro["densidade_media_ego"],
            color="steelblue",
            edgecolor="navy",
            linewidth=1.2,
            height=0.7,
        )

        ax.set_yticks(y_positions)
        ax.set_yticklabels(density_by_micro["microrregiao"])

        for idx, (_, row) in enumerate(density_by_micro.iterrows()):
            ax.text(
                row["densidade_media_ego"] + 0.01,
                idx,
                f"{row['densidade_media_ego']:.3f}",
                va="center",
                fontsize=9,
            )

        ax.set_xlabel("Densidade Média de Ego-Network", fontweight="bold")
        ax.set_ylabel("Microrregião", fontweight="bold")
        ax.set_title(
            "Ranking de Densidade de Ego-Network por Microrregião\n"
            + "Mede o quão interconectados são os vizinhos de cada bairro",
            fontweight="bold",
            pad=20,
        )
        ax.set_xlim(0, density_by_micro["densidade_media_ego"].max() * 1.15)

        plt.tight_layout()
        output_path = self.output_dir / "ranking_densidade_microrregiao.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        csv_path = self.output_dir / "ranking_densidade_microrregiao.csv"
        density_by_micro.to_csv(csv_path, index=False, encoding="utf-8")

        self._create_html_wrapper(
            "ranking_densidade_microrregiao.png",
            "Ranking de Densidade por Microrregião",
            "ranking_densidade_microrregiao.html",
        )

        return density_by_micro

    def viz_subgraph_top10_neighborhoods(
        self, graph: Graph, ego_path: str = EGO_BAIRRO_PATH
    ) -> None:
        ego_df = pd.read_csv(ego_path)

        top10 = ego_df.nlargest(10, "grau")
        top10_bairros = set(top10["bairro"].str.strip().str.title())

        subgraph = graph.get_subgraph(top10_bairros)

        self._create_static_subgraph_plot(subgraph, top10)

    def _create_static_subgraph_plot(
        self, subgraph: Graph, top10: pd.DataFrame
    ) -> None:

        fig, ax = plt.subplots(figsize=(14, 10))

        vertices = list(subgraph.get_vertices())
        n = len(vertices)

        positions = {}
        import math

        for i, v in enumerate(vertices):
            angle = 2 * math.pi * i / n
            positions[v] = (math.cos(angle), math.sin(angle))

        for u in vertices:
            for v in subgraph.get_neighbors(u):
                if u < v:
                    x1, y1 = positions[u]
                    x2, y2 = positions[v]
                    ax.plot(
                        [x1, x2], [y1, y2], "gray", alpha=0.5, linewidth=2, zorder=1
                    )

        degrees = dict(top10[["bairro", "grau"]].values)

        for v in vertices:
            x, y = positions[v]
            degree = degrees.get(v, 1)

            size = 500 + degree * 200
            if degree >= 9:
                color = "#FC2103"
            elif degree >= 8:
                color = "#FF6929"
            elif degree >= 7:
                color = "#FFF538"
            else:
                color = "#FDF4E3"

            ax.scatter(
                x,
                y,
                s=size,
                c=color,
                edgecolors="black",
                linewidths=2,
                zorder=2,
                alpha=0.8,
            )
            ax.text(
                x,
                y,
                v.replace(" ", "\n"),
                fontsize=9,
                fontweight="bold",
                ha="center",
                va="center",
                zorder=3,
            )

        ax.set_title(
            "Subgrafo dos 10 Bairros com Maior Grau (Hubs da Cidade)\n"
            + "Tamanho e cor dos nós = grau (número de conexões)",
            fontweight="bold",
            fontsize=14,
            pad=20,
        )
        ax.axis("equal")
        ax.axis("off")

        legend_text = "\n".join(
            [f"{row['bairro']}: {row['grau']} conexões" for _, row in top10.iterrows()]
        )
        ax.text(
            1.35,
            0.5,
            legend_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="center",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
        )

        plt.tight_layout()
        output_path = self.output_dir / "subgrafo_top10_bairros.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        self._create_html_wrapper(
            "subgrafo_top10_bairros.png",
            "Subgrafo Top 10 Bairros",
            "subgrafo_top10_bairros.html",
        )

    def viz_degree_distribution_histogram(
        self, ego_path: str = EGO_BAIRRO_PATH
    ) -> None:
        ego_df = pd.read_csv(ego_path)
        graus = ego_df["grau"]

        stats = {
            "média": graus.mean(),
            "mediana": graus.median(),
            "mínimo": graus.min(),
            "máximo": graus.max(),
            "desvio_padrão": graus.std(),
        }

        fig, ax = plt.subplots(figsize=(16, 6))

        n, bins, patches = ax.hist(
            graus,
            bins=range(int(graus.min()), int(graus.max()) + 2),
            color="skyblue",
            edgecolor="navy",
            linewidth=1.5,
            alpha=0.7,
        )

        cm = plt.cm.RdYlGn_r
        norm = plt.Normalize(vmin=n.min(), vmax=n.max())
        for count, patch in zip(n, patches):
            patch.set_facecolor(cm(norm(count)))

        ax.axvline(
            stats["média"],
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Média: {stats['média']:.2f}",
        )
        ax.axvline(
            stats["mediana"],
            color="green",
            linestyle="--",
            linewidth=2,
            label=f"Mediana: {stats['mediana']:.1f}",
        )

        ax.set_xlabel("Grau (Número de Conexões)", fontweight="bold")
        ax.set_ylabel("Frequência (Número de Bairros)", fontweight="bold")
        ax.set_title(
            "Distribuição de Graus dos Bairros do Recife\n"
            + "Mostra quantos vizinhos diretos cada bairro possui",
            fontweight="bold",
        )
        ax.legend(loc="upper right")
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "histograma_distribuicao_graus.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        self._create_html_wrapper(
            "histograma_distribuicao_graus.png",
            "Histograma de Distribuição de Graus",
            "histograma_distribuicao_graus.html",
        )

        return stats

    def viz_path_tree(self, caminho: str, origem: str, destino: str, custo: float):
        lista = caminho.split("->")
        bairros = [b.strip() for b in lista]
        n = len(bairros)

        _, ax = plt.subplots(figsize=(16, 10))

        positions = {}
        for i, bairro in enumerate(bairros):
            x = i * 2
            y = 0
            positions[bairro] = (x, y)

        for i in range(len(bairros) - 1):
            u = bairros[i]
            v = bairros[i + 1]
            x1, y1 = positions[u]
            x2, y2 = positions[v]

            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    color="darkblue",
                    lw=5,
                    alpha=0.7,
                ),
                zorder=1,
            )

        for i, bairro in enumerate(bairros):
            x, y = positions[bairro]

            if i == 0:
                color = "#4CAF50"
            elif i == n - 1:
                color = "#F44336"
            else:
                color = "#2196F3"
            if len(bairro.split()) > 1:
                label = "\n".join(bairro.split())
            else:
                label = bairro

            ax.scatter(x, y, s=5000, c=color, edgecolors="black", zorder=2, alpha=0.9)

            ax.text(
                x,
                y,
                label,
                fontsize=11,
                fontweight="bold",
                ha="center",
                va="center",
                zorder=3,
                color="black",
            )

        ax.set_title(
            f"Árvore de Caminho: {origem} → {destino}\n"
            f"Custo Total: {custo:.1f} | Número de Passos: {n - 1}",
            fontweight="bold",
            fontsize=14,
            pad=20,
        )

        ax.axis("equal")
        ax.axis("off")

        margin = 1.5
        ax.set_xlim(-margin, (n - 1) * 2 + margin)
        ax.set_ylim(-margin * 3, margin * 3)

        plt.tight_layout()
        q7_dir = Path(PART1_Q7_DIR)
        q7_dir.mkdir(parents=True, exist_ok=True)
        output_path = q7_dir / "arvore_percurso.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        q7_html = q7_dir / "arvore_percurso.html"
        self._create_html_wrapper(
            "arvore_percurso.png",
            f"Árvore de Percurso: {origem} → {destino}",
            str(q7_html),
            is_q7=True,
        )

        print(f"Visualização salva em: {output_path}")

    def viz_interactive_graph(
        self,
        graph: Graph,
        ego_path: str = EGO_BAIRRO_PATH,
        bairros_path: str = BAIRROS_UNIQUE_PATH,
        caminho_destacado: list = None,
    ):

        ego_df = pd.read_csv(ego_path)
        bairros_df = pd.read_csv(bairros_path)

        ego_df["bairro"] = ego_df["bairro"].apply(normalize_name)
        bairros_df["bairro"] = bairros_df["bairro"].apply(normalize_name)

        merged = ego_df.merge(bairros_df, on="bairro", how="left")

        info_bairros = {}
        for _, row in merged.iterrows():
            info_bairros[row["bairro"]] = {
                "grau": row["grau"],
                "microrregiao": row.get("microrregiao", "N/A"),
                "densidade_ego": row["densidade_ego"],
            }

        net = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            notebook=False,
            cdn_resources="in_line",
            select_menu=True,
            filter_menu=False,
        )

        net.set_options(
            """
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000,
              "centralGravity": 0.3,
              "springLength": 150,
              "springConstant": 0.04,
              "damping": 0.09,
              "avoidOverlap": 0.5
            },
            "minVelocity": 0.75
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100
          }
        }
        """
        )

        caminho_set = set(caminho_destacado) if caminho_destacado else set()

        for vertice in graph.get_vertices():
            info = info_bairros.get(
                vertice, {"grau": 0, "microrregiao": "N/A", "densidade_ego": 0.0}
            )

            titulo = f"""
            {vertice}
            Grau: {info['grau']}
            Microrregião: {info['microrregiao']}
            Densidade Ego: {info['densidade_ego']:.3f}
            """

            grau = info["grau"]
            tamanho = 20 + grau * 3

            if vertice in caminho_set:
                cor = "#FF4444"
                tamanho = tamanho * 1.5
            elif grau >= 8:
                cor = "#FFA500"
            elif grau >= 5:
                cor = "#4CAF50"
            else:
                cor = "#2196F3"

            net.add_node(vertice, label=vertice, title=titulo, size=tamanho, color=cor)

        for u in graph.get_vertices():
            for v in graph.get_neighbors(u):
                peso = graph.get_weight(u, v)

                if caminho_destacado and len(caminho_destacado) > 1:
                    for i in range(len(caminho_destacado) - 1):
                        if (
                            u == caminho_destacado[i] and v == caminho_destacado[i + 1]
                        ) or (
                            v == caminho_destacado[i] and u == caminho_destacado[i + 1]
                        ):
                            net.add_edge(u, v, value=peso, color="#FF0000", width=5)
                            break
                    else:
                        net.add_edge(u, v, value=peso, color="#999999", width=1)
                else:
                    net.add_edge(u, v, value=peso, color="#999999", width=1)

        q9_dir = Path(PART1_Q9_DIR)
        q9_dir.mkdir(parents=True, exist_ok=True)
        output_path = q9_dir / "grafo_interativo.html"

        net.save_graph(str(output_path))
        self._customize_html(output_path, caminho_destacado)

        print(f"Grafo interativo salvo em: {output_path}")
        return str(output_path)

    def _create_html_wrapper(
        self, image_filename: str, title: str, output_filename: str, is_q7: bool = False
    ):
        if is_q7:
            img_path = image_filename
        else:
            img_path = image_filename

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Grafos Recife</title>
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
        nav a {{
            color: white !important;
            text-decoration: none;
            padding: 1rem;
            display: inline-block;
        }}
        nav a:hover {{
            background-color: #555;
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
            <a href="../1.9 Apresentação interativa do grafo/grafo_interativo.html">Grafo Interativo</a>
            <a href="../1.7 Transforme o percurso em árvore e mostre/arvore_percurso.html">Árvore de Percurso</a>
            <a href="../1.8 Explorações e visualizações analíticas/histograma_distribuicao_graus.html"
            >Histograma de Distribuição de Graus</a
            >
            <a href="../1.8 Explorações e visualizações analíticas/ranking_densidade_microrregiao.html"
            >Ranking de Densidade por Microrregião</a
            >
            <a href="../1.8 Explorações e visualizações analíticas/subgrafo_top10_bairros.html">Subgrafo Top 10 Bairros</a>
            <a href="../../2. Dataset Maior e Comparação de Algoritmos/report.html">Relatório de Testes</a>
        </nav>
    </header>

    <div class="container">
        <h1>{title}</h1>
        <div class="image-container">
            <img src="{img_path}" alt="{title}">
        </div>
    </div>
</body>
</html>"""

        if is_q7:
            output_path = Path(output_filename)
        else:
            output_path = self.output_dir / output_filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _customize_html(self, html_path: Path, caminho: list = None):

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r"\s*<center>\s*<h1>\s*</h1>\s*</center>\s*", "", content)

        caminho_texto = " → ".join(caminho) if caminho else "N/A"

        custom_html = f"""
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
            nav a {{
                color: white !important;
                text-decoration: none;
                padding: 1rem;
                display: inline-block;
            }}
            nav a:hover {{
                background-color: #555;
            }}
            .header {{
                background: #667eea;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0 0 10px 0;
            }}
            .legenda {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .legenda h3 {{
                margin-top: 0;
            }}
            .legenda-item {{
                display: inline-block;
                margin-right: 20px;
                margin-bottom: 10px;
            }}
            .legenda-cor {{
                display: inline-block;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 5px;
                vertical-align: middle;
            }}
            .caminho-destaque {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }}
        </style>
        <header>
            <nav>
                <a href="../1.9 Apresentação interativa do grafo/grafo_interativo.html">Grafo Interativo</a>
                <a href="../1.7 Transforme o percurso em árvore e mostre/arvore_percurso.html">Árvore de Percurso</a>
                <a href="../1.8 Explorações e visualizações analíticas/histograma_distribuicao_graus.html"
                >Histograma de Distribuição de Graus</a
                >
                <a href="../1.8 Explorações e visualizações analíticas/ranking_densidade_microrregiao.html"
                >Ranking de Densidade por Microrregião</a
                >
                <a href="../1.8 Explorações e visualizações analíticas/subgrafo_top10_bairros.html">Subgrafo Top 10 Bairros</a>
                <a href="../../2. Dataset Maior e Comparação de Algoritmos/report.html">Relatório de Testes</a>
            </nav>
        </header>
        <div class="header">
            <h1>Grafo Interativo - Bairros do Recife</h1>
            <p>Análise de conectividade entre bairros da cidade</p>
        </div>
        <div class="legenda">
            <h3>Legenda</h3>
            <div class="legenda-item">
                <span class="legenda-cor" style="background: #FF4444;"></span>
                <strong>Vermelho:</strong> Caminho destacado
            </div>
            <div class="legenda-item">
                <span class="legenda-cor" style="background: #FFA500;"></span>
                <strong>Laranja:</strong> Hubs (≥8 conexões)
            </div>
            <div class="legenda-item">
                <span class="legenda-cor" style="background: #4CAF50;"></span>
                <strong>Verde:</strong> Bem conectados (5-7 conexões)
            </div>
            <div class="legenda-item">
                <span class="legenda-cor" style="background: #2196F3;"></span>
                <strong>Azul:</strong> Conexões normais (<5)
            </div>
            <div class="caminho-destaque">
                <strong>🚩 Caminho Destacado:</strong> {caminho_texto}
            </div>
        </div>
        """

        content = content.replace("<body>", f"<body>{custom_html}")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    from solve import GraphAnalyzer

    analyzer = GraphAnalyzer()
    adjacencies_df = analyzer.load_adjacencies()
    analyzer.load_neighborhoods_microregions()
    graph = analyzer.build_graph(adjacencies_df)

    visualizer = GraphVisualizer()

    visualizer.viz_ranking_density_ego_per_microregion()
    visualizer.viz_subgraph_top10_neighborhoods(graph)
    visualizer.viz_degree_distribution_histogram()


if __name__ == "__main__":
    main()
