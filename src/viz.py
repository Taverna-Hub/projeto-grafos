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
            select_menu=False,
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

            # Adicionar grau como atributo personalizado para acesso no JavaScript
            net.add_node(
                vertice, label=vertice, title=titulo, size=tamanho, color=cor, grau=grau
            )

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
        self._customize_html(output_path, caminho_destacado, info_bairros)

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
        nav {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .menu-item {{
            position: relative;
            display: inline-block;
        }}
        .menu-item > a {{
            color: white !important;
            text-decoration: none;
            padding: 1rem;
            display: inline-block;
        }}
        .menu-item:hover > a {{
            background-color: #555;
        }}
        .submenu {{
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            background-color: #444;
            min-width: 300px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            z-index: 1;
        }}
        .submenu a {{
            color: white !important;
            text-decoration: none;
            padding: 12px 16px;
            display: block;
            text-align: left;
        }}
        .submenu a:hover {{
            background-color: #555;
        }}
        .menu-item:hover .submenu {{
            display: block;
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
            <div class="menu-item">
                <a href="#">Grafo dos Bairros do Recife</a>
                <div class="submenu">
                    <a href="../1.9 Apresentação interativa do grafo/grafo_interativo.html">Grafo Interativo</a>
                    <a href="../1.7 Transforme o percurso em árvore e mostre/arvore_percurso.html">Árvore de Percurso</a>
                    <a href="../1.8 Explorações e visualizações analíticas/histograma_distribuicao_graus.html">Histograma de Distribuição de Graus</a>
                    <a href="../1.8 Explorações e visualizações analíticas/ranking_densidade_microrregiao.html">Ranking de Densidade por Microrregião</a>
                    <a href="../1.8 Explorações e visualizações analíticas/subgrafo_top10_bairros.html">Subgrafo Top 10 Bairros</a>
                </div>
            </div>
            <div class="menu-item">
                <a href="#">Dataset de Histórico de Transações Bitcoin</a>
                <div class="submenu">
                    <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_degree_distribution.html">Distribuição de Graus</a>
                    <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_distance_heatmap.html">Mapa de Distâncias</a>
                    <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_graph_sample.html">Amostra do Grafo</a>
                    <a href="../../2. Dataset Maior e Comparação de Algoritmos/report.html">Relatório de Testes</a>
                </div>
            </div>
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

    def _customize_html(
        self, html_path: Path, caminho: list = None, info_bairros: dict = None
    ):

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r"\s*<center>\s*<h1>\s*</h1>\s*</center>\s*", "", content)

        caminho_texto = " → ".join(caminho) if caminho else "N/A"

        bairros_list = sorted(info_bairros.keys()) if info_bairros else []
        bairros_options = "".join(
            [f'<option value="{b}">{b}</option>' for b in bairros_list]
        )

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
            nav {{
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .menu-item {{
                position: relative;
                display: inline-block;
            }}
            .menu-item > a {{
                color: white !important;
                text-decoration: none;
                padding: 1rem;
                display: inline-block;
            }}
            .menu-item:hover > a {{
                background-color: #555;
            }}
            .submenu {{
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                background-color: #444;
                min-width: 300px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                z-index: 1;
            }}
            .submenu a {{
                color: white !important;
                text-decoration: none;
                padding: 12px 16px;
                display: block;
                text-align: left;
            }}
            .submenu a:hover {{
                background-color: #555;
            }}
            .menu-item:hover .submenu {{
                display: block;
            }}
            .content-section {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .page-title {{
                text-align: center;
                padding: 30px 20px;
            }}
            .page-title h1 {{
                margin: 0;
                color: #333;
                font-size: 32px;
                font-weight: bold;
            }}
            .page-title p {{
                margin: 10px 0 0 0;
                color: #666;
                font-size: 16px;
            }}
            .graph-section {{
                min-height: calc(600px + 40px);
            }}
            .graph-section #mynetwork {{
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                height: 600px;
            }}
            .legenda-section h3 {{
                margin-top: 0px;
                margin-bottom: 15px;
                color: #333;
            }}
            .select-node-section {{
                padding: 20px;
            }}
            .select-node-section h3 {{
                margin-top: 0;
                margin-bottom: 15px;
                color: #333;
            }}
            .select-controls {{
                display: flex;
                gap: 10px;
                align-items: center;
                flex-wrap: wrap;
            }}
            #nodeSelect {{
                padding: 10px 15px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                min-width: 300px;
                flex: 1;
                max-width: 500px;
                cursor: pointer;
                background: white;
                font-family: Arial, sans-serif;
                appearance: none;
                -webkit-appearance: none;
                -moz-appearance: none;
                background-image: url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"%3e%3cpolyline points="6 9 12 15 18 9"%3e%3c/polyline%3e%3c/svg%3e');
                background-repeat: no-repeat;
                background-position: right 10px center;
                background-size: 20px;
                padding-right: 40px;
            }}
            #nodeSelect:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            #nodeSelect option {{
                padding: 10px;
                font-size: 14px;
            }}
            #nodeSelect option:hover {{
                background-color: #f0f0f0;
            }}
            #resetNodeSelection {{
                padding: 10px 20px;
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
            }}
            #resetNodeSelection:hover {{
                background: #1976D2;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }}
            #resetNodeSelection:active {{
                background: #1565C0;
                transform: translateY(1px);
            }}
            .path-finder-section h3 {{
                margin-top: 0;
                margin-bottom: 15px;
                color: #333;
            }}
            .path-controls {{
                display: flex;
                gap: 15px;
                align-items: flex-end;
                flex-wrap: wrap;
                margin-bottom: 15px;
            }}
            .path-control-group {{
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}
            .path-control-group label {{
                font-weight: bold;
                font-size: 14px;
                color: #555;
            }}
            .path-control-group select {{
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
                cursor: pointer;
            }}
            .path-control-group select:focus {{
                outline: none;
                border-color: #667eea;
            }}
            .vis-network {{
                outline: none;
            }}
            .vis-network {{
                outline: none;
            }}
            .button-group {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            #calcularCaminho {{
                padding: 10px 25px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }}
            #calcularCaminho:hover {{
                background: #5568d3;
            }}
            #calcularCaminho:active {{
                background: #4450b0;
            }}
            #resetarCaminho {{
                padding: 10px 25px;
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }}
            #resetarCaminho:hover {{
                background: #5a6268;
            }}
            #resetarCaminho:active {{
                background: #4e555b;
            }}
            #resultadoCaminho {{
                margin-top: 15px;
                padding: 15px;
                background: #e8f4f8;
                border-left: 4px solid #2196F3;
                border-radius: 5px;
                display: none;
            }}
            #resultadoCaminho.show {{
                display: block;
            }}
            #resultadoCaminho.error {{
                background: #ffe8e8;
                border-left-color: #f44336;
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
        </style>
        <header>
            <nav>
                <div class="menu-item">
                    <a href="#">Grafo dos Bairros do Recife</a>
                    <div class="submenu">
                        <a href="../1.9 Apresentação interativa do grafo/grafo_interativo.html">Grafo Interativo</a>
                        <a href="../1.7 Transforme o percurso em árvore e mostre/arvore_percurso.html">Árvore de Percurso</a>
                        <a href="../1.8 Explorações e visualizações analíticas/histograma_distribuicao_graus.html">Histograma de Distribuição de Graus</a>
                        <a href="../1.8 Explorações e visualizações analíticas/ranking_densidade_microrregiao.html">Ranking de Densidade por Microrregião</a>
                        <a href="../1.8 Explorações e visualizações analíticas/subgrafo_top10_bairros.html">Subgrafo Top 10 Bairros</a>
                    </div>
                </div>
                <div class="menu-item">
                    <a href="#">Dataset de Histórico de Transações Bitcoin</a>
                    <div class="submenu">
                        <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_degree_distribution.html">Distribuição de Graus</a>
                        <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_distance_heatmap.html">Mapa de Distâncias</a>
                        <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_graph_sample.html">Amostra do Grafo</a>
                        <a href="../../2. Dataset Maior e Comparação de Algoritmos/bitcoin_graph_sample_interactive.html">Grafo Interativo</a>
                        <a href="../../2. Dataset Maior e Comparação de Algoritmos/report.html">Relatório de Testes</a>
                    </div>
                </div>
            </nav>
        </header>

        <div style="display: flex; justify-content: space-between">
            <div class="content-section select-node-section">
                <h3>🔍 Selecione um nó para visualizar sua vizinhança</h3>
                <div class="select-controls">
                    <select id="nodeSelect">
                        <option value="">-- Selecione um bairro --</option>
                        {bairros_options}
                    </select>
                    <button id="resetNodeSelection">Resetar Seleção</button>
                </div>
            </div>
            
            <div class="content-section path-finder-section">
                <h3>🗺️ Calcular Novo Percurso</h3>
                <div class="path-controls">
                    <div class="path-control-group">
                        <label for="origemSelect">Bairro de Origem:</label>
                        <select id="origemSelect">
                            <option value="">-- Selecione --</option>
                            {bairros_options}
                        </select>
                    </div>
                    <div class="path-control-group">
                        <label for="destinoSelect">Bairro de Destino:</label>
                        <select id="destinoSelect">
                            <option value="">-- Selecione --</option>
                            {bairros_options}
                        </select>
                    </div>
                    <button id="calcularCaminho">Calcular Caminho Mais Curto</button>
                    <button id="resetarCaminho">Resetar para Padrão</button>
                </div>
                <div id="resultadoCaminho"></div>
            </div>
        </div>
        
        
        <div class="content-section">
            <div class="graph-section" id="graph-container"></div>
            
            <div class="legenda-section">
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
            </div>
        </div>
 
        <script>
            window.addEventListener('DOMContentLoaded', function() {{
                const mynetwork = document.getElementById('mynetwork');
                if (mynetwork) {{
                    const graphContainer = document.getElementById('graph-container');
                    graphContainer.appendChild(mynetwork);
                }}
                
                document.getElementById('origemSelect').value = 'Nova Descoberta';
                document.getElementById('destinoSelect').value = 'Boa Viagem (Setúbal)';
                document.getElementById('calcularCaminho').click();
            }});
            
            document.getElementById('nodeSelect').addEventListener('change', function() {{
                const selectedNode = this.value;
                if (!selectedNode) return;
                
                const edges = network.body.data.edges;
                const neighbors = new Set();
                
                edges.forEach(edge => {{
                    if (edge.from === selectedNode) {{
                        neighbors.add(edge.to);
                    }}
                    if (edge.to === selectedNode) {{
                        neighbors.add(edge.from);
                    }}
                }});
                
                network.body.data.nodes.forEach(node => {{
                    const info = node.grau !== undefined ? node.grau : 0;
                    let cor, tamanho, opacity;
                    
                    if (node.id === selectedNode) {{
                        if (info >= 8) cor = '#FFA500';
                        else if (info >= 5) cor = '#4CAF50';
                        else cor = '#2196F3';
                        tamanho = 20 + info * 3;
                        opacity = 1;
                    }} else if (neighbors.has(node.id)) {{
                        cor = '#FF4444';
                        tamanho = (20 + info * 3) * 1.3;
                        opacity = 1;
                    }} else {{
                        if (info >= 8) cor = '#FFA500';
                        else if (info >= 5) cor = '#4CAF50';
                        else cor = '#2196F3';
                        tamanho = 20 + info * 3;
                        opacity = 0.2;
                    }}
                    
                    network.body.data.nodes.update({{
                        id: node.id,
                        color: {{ background: cor, border: cor }},
                        size: tamanho,
                        opacity: opacity
                    }});
                }});
                
                network.body.data.edges.forEach(edge => {{
                    if (edge.from === selectedNode || edge.to === selectedNode) {{
                        network.body.data.edges.update({{
                            id: edge.id,
                            color: '#999999',
                            width: 3
                        }});
                    }} else {{
                        network.body.data.edges.update({{
                            id: edge.id,
                            color: {{ color: '#999999', opacity: 0.1 }},
                            width: 1
                        }});
                    }}
                }});
                
                network.focus(selectedNode, {{
                    scale: 1.1,
                    animation: {{
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }}
                }});
            }});
            
            document.getElementById('resetNodeSelection').addEventListener('click', function() {{
                document.getElementById('nodeSelect').value = '';
                
                network.body.data.nodes.forEach(node => {{
                    const info = node.grau !== undefined ? node.grau : 0;
                    let cor = '#2196F3';
                    if (info >= 8) cor = '#FFA500';
                    else if (info >= 5) cor = '#4CAF50';
                    
                    network.body.data.nodes.update({{
                        id: node.id,
                        color: cor,
                        size: 20 + info * 3,
                        opacity: 1
                    }});
                }});
                
                network.body.data.edges.forEach(edge => {{
                    network.body.data.edges.update({{
                        id: edge.id,
                        color: '#999999',
                        width: 1
                    }});
                }});
                
                network.fit({{
                    animation: {{
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }}
                }});
            }});
            
            // Implementação do algoritmo de Dijkstra
            function dijkstra(network, origem, destino) {{
                const nodes = network.body.data.nodes;
                const edges = network.body.data.edges;
                
                // Construir grafo de adjacências
                const grafo = {{}};
                edges.forEach(edge => {{
                    if (!grafo[edge.from]) grafo[edge.from] = [];
                    if (!grafo[edge.to]) grafo[edge.to] = [];
                    
                    const peso = edge.value || 1;
                    grafo[edge.from].push({{ node: edge.to, peso: peso }});
                    grafo[edge.to].push({{ node: edge.from, peso: peso }});
                }});
                
                // Inicializar distâncias
                const distancias = {{}};
                const anteriores = {{}};
                const visitados = new Set();
                const fila = [];
                
                nodes.forEach(node => {{
                    distancias[node.id] = Infinity;
                    anteriores[node.id] = null;
                }});
                
                distancias[origem] = 0;
                fila.push({{ node: origem, dist: 0 }});
                
                while (fila.length > 0) {{
                    // Ordenar fila por distância
                    fila.sort((a, b) => a.dist - b.dist);
                    const {{ node: atual }} = fila.shift();
                    
                    if (visitados.has(atual)) continue;
                    visitados.add(atual);
                    
                    if (atual === destino) break;
                    
                    if (!grafo[atual]) continue;
                    
                    grafo[atual].forEach(vizinho => {{
                        if (visitados.has(vizinho.node)) return;
                        
                        const novaDist = distancias[atual] + vizinho.peso;
                        if (novaDist < distancias[vizinho.node]) {{
                            distancias[vizinho.node] = novaDist;
                            anteriores[vizinho.node] = atual;
                            fila.push({{ node: vizinho.node, dist: novaDist }});
                        }}
                    }});
                }}
                
                // Reconstruir caminho
                if (distancias[destino] === Infinity) {{
                    return null;
                }}
                
                const caminho = [];
                let atual = destino;
                while (atual !== null) {{
                    caminho.unshift(atual);
                    atual = anteriores[atual];
                }}
                
                return {{
                    caminho: caminho,
                    custo: distancias[destino]
                }};
            }}
            
            // Handler do botão
            document.getElementById('calcularCaminho').addEventListener('click', function() {{
                const origem = document.getElementById('origemSelect').value;
                const destino = document.getElementById('destinoSelect').value;
                const resultado = document.getElementById('resultadoCaminho');
                
                if (!origem || !destino) {{
                    resultado.className = 'error show';
                    resultado.innerHTML = '<strong>⚠️ Erro:</strong> Por favor, selecione origem e destino.';
                    return;
                }}
                
                if (origem === destino) {{
                    resultado.className = 'error show';
                    resultado.innerHTML = '<strong>⚠️ Erro:</strong> Origem e destino devem ser diferentes.';
                    return;
                }}
                
                // Calcular caminho
                const pathResult = dijkstra(network, origem, destino);
                
                if (!pathResult) {{
                    resultado.className = 'error show';
                    resultado.innerHTML = '<strong>❌ Erro:</strong> Não existe caminho entre esses bairros.';
                    return;
                }}
                
                // Resetar cores anteriores
                network.body.data.nodes.forEach(node => {{
                    const info = node.grau !== undefined ? node.grau : 0;
                    let cor = '#2196F3';
                    if (info >= 8) cor = '#FFA500';
                    else if (info >= 5) cor = '#4CAF50';
                    
                    network.body.data.nodes.update({{
                        id: node.id,
                        color: cor,
                        size: 20 + info * 3
                    }});
                }});
                
                network.body.data.edges.forEach(edge => {{
                    network.body.data.edges.update({{
                        id: edge.id,
                        color: '#999999',
                        width: 1
                    }});
                }});
                
                // Destacar caminho
                pathResult.caminho.forEach(nodeId => {{
                    const node = network.body.data.nodes.get(nodeId);
                    const info = node.grau !== undefined ? node.grau : 0;
                    network.body.data.nodes.update({{
                        id: nodeId,
                        color: '#FF4444',
                        size: (20 + info * 3) * 1.5
                    }});
                }});
                
                // Destacar arestas do caminho
                for (let i = 0; i < pathResult.caminho.length - 1; i++) {{
                    const from = pathResult.caminho[i];
                    const to = pathResult.caminho[i + 1];
                    
                    const edge = network.body.data.edges.get({{
                        filter: function(item) {{
                            return (item.from === from && item.to === to) || 
                                   (item.from === to && item.to === from);
                        }}
                    }})[0];
                    
                    if (edge) {{
                        network.body.data.edges.update({{
                            id: edge.id,
                            color: '#FF0000',
                            width: 5
                        }});
                    }}
                }}
                
                // Mostrar resultado
                resultado.className = 'show';
                resultado.innerHTML = `
                    <strong>✅ Caminho Encontrado!</strong><br>
                    <strong>Percurso:</strong> ${{pathResult.caminho.join(' → ')}}<br>
                    <strong>Número de passos:</strong> ${{pathResult.caminho.length - 1}}<br>
                    <strong>Custo total:</strong> ${{pathResult.custo.toFixed(2)}}
                `;
            }});
            
            // Handler do botão resetar
            document.getElementById('resetarCaminho').addEventListener('click', function() {{
                document.getElementById('origemSelect').value = 'Nova Descoberta';
                document.getElementById('destinoSelect').value = 'Boa Viagem (Setúbal)';
                document.getElementById('calcularCaminho').click();
            }});
        </script>
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
