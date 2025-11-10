import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utils.normalize import normalize_name

from graphs.graph import Graph
from constants import EGO_BAIRRO_PATH, BAIRROS_UNIQUE_PATH, OUT_DIR


class GraphVisualizer:

    def __init__(self, output_dir: str = OUT_DIR):
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

        bairros_df["bairro"].apply(normalize_name)
        ego_df["bairro"].apply(normalize_name)

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

        fig, ax = plt.subplots(figsize=(14, 8))

        bars = ax.barh(
            density_by_micro["microrregiao"],
            density_by_micro["densidade_media_ego"],
            color="steelblue",
            edgecolor="navy",
            linewidth=1.2,
        )

        for i, (idx, row) in enumerate(density_by_micro.iterrows()):
            ax.text(
                row["densidade_media_ego"] + 0.01,
                i,
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
            if degree >= 8:
                color = "#ff4444"
            elif degree >= 6:
                color = "#ffaa00"
            else:
                color = "#44aa44"

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
                v,
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

    def viz_histograma_distribuicao_graus(
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

        return stats


def main():
    from solve import GraphAnalyzer

    analyzer = GraphAnalyzer()
    adjacencies_df = analyzer.load_adjacencies()
    analyzer.load_neighborhoods_microregions()
    graph = analyzer.build_graph(adjacencies_df)

    visualizer = GraphVisualizer()

    visualizer.viz_ranking_density_ego_per_microregion()
    visualizer.viz_subgraph_top10_neighborhoods(graph)
    visualizer.viz_histograma_distribuicao_graus()


if __name__ == "__main__":
    main()
