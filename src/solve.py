import json
import os
import csv
from pathlib import Path
from typing import Dict, List, Set
import pandas as pd
from graphs.graph import Graph


def normalize_name(name: str) -> str:
    if pd.isna(name) or name is None:
        return None

    name = str(name).strip()
    return " ".join(name.title().split())


def load_adjacencies(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding="utf-8")

    df["bairro_origem"] = df["bairro_origem"].apply(normalize_name)
    df["bairro_destino"] = df["bairro_destino"].apply(normalize_name)

    df = df.dropna(subset=["bairro_origem", "bairro_destino"])

    return df


def load_neighborhoods_microregions(filepath: str) -> Dict[str, str]:
    df = pd.read_csv(filepath, encoding="utf-8")
    df["bairro"] = df["bairro"].apply(normalize_name)
    df = df.drop_duplicates(subset=["bairro"], keep="first")

    mapping = dict(zip(df["bairro"], df["microrregiao"]))

    return mapping


def build_graph(adjacencies_df: pd.DataFrame) -> Graph:
    graph = Graph()

    for _, row in adjacencies_df.iterrows():
        origem = row["bairro_origem"]
        destino = row["bairro_destino"]
        peso = row.get("peso", 1.0)

        if pd.isna(peso):
            peso = 1.0
        else:
            peso = float(peso)

        graph.add_edge(origem, destino, peso)

    return graph


def compute_global_metrics(graph: Graph) -> Dict:
    metrics = graph.get_metrics()
    result = metrics.to_dict()

    return result


def compute_microregion_metrics(
    graph: Graph, neighborhood_microregions: Dict[str, str]
) -> List[Dict]:
    microregion_neighborhoods: Dict[str, Set[str]] = {}

    for bairro, microregion in neighborhood_microregions.items():
        if microregion not in microregion_neighborhoods:
            microregion_neighborhoods[microregion] = set()
        microregion_neighborhoods[microregion].add(bairro)

    results = []

    for microregion in sorted(microregion_neighborhoods.keys()):
        neighborhoods = microregion_neighborhoods[microregion]

        neighborhoods_in_graph = {n for n in neighborhoods if graph.has_node(n)}

        if not neighborhoods_in_graph:
            continue

        subgraph = graph.get_subgraph(neighborhoods_in_graph)
        metrics = subgraph.get_metrics()

        result = {
            "microrregiao": microregion,
            "bairros": sorted(list(neighborhoods_in_graph)),
            "ordem": metrics.ordem,
            "tamanho": metrics.tamanho,
            "densidade": metrics.densidade,
        }

        results.append(result)

    return results


def compute_ego_metrics(graph: Graph) -> List[Dict]:
    results = []

    for bairro in sorted(graph.get_vertices()):
        grau = graph.get_degree(bairro)

        ego_graph = graph.get_ego_network(bairro)
        ego_metrics = ego_graph.get_metrics()

        result = {
            "bairro": bairro,
            "grau": grau,
            "ordem_ego": ego_metrics.ordem,
            "tamanho_ego": ego_metrics.tamanho,
            "densidade_ego": ego_metrics.densidade,
        }

        results.append(result)

    return results


def save_results(
    global_metrics: Dict,
    microregion_metrics: List[Dict],
    ego_metrics: List[Dict],
    output_dir: str = "out",
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    global_path = Path(output_dir) / "recife_global.json"
    with open(global_path, "w", encoding="utf-8") as f:
        json.dump(global_metrics, f, indent=2, ensure_ascii=False)

    microregion_path = Path(output_dir) / "microrregioes.json"
    with open(microregion_path, "w", encoding="utf-8") as f:
        json.dump(microregion_metrics, f, indent=2, ensure_ascii=False)

    ego_path = Path(output_dir) / "ego_bairro.csv"
    with open(ego_path, "w", encoding="utf-8", newline="") as f:
        if ego_metrics:
            fieldnames = ["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ego_metrics)


def main():
    adjacencies_path = "data/adjacencias_bairros.csv"
    neighborhoods_path = "data/bairros_unique.csv"

    adjacencies_df = load_adjacencies(adjacencies_path)
    neighborhood_microregions = load_neighborhoods_microregions(neighborhoods_path)

    graph = build_graph(adjacencies_df)

    global_metrics = compute_global_metrics(graph)
    microregion_metrics = compute_microregion_metrics(graph, neighborhood_microregions)
    ego_metrics = compute_ego_metrics(graph)

    save_results(global_metrics, microregion_metrics, ego_metrics)


if __name__ == "__main__":
    main()
