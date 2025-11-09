import csv
import json
import pandas as pd
from pathlib import Path
from graphs.graph import Graph
from utils.normalize import normalize_name
from typing import Dict, List, Set, Optional

from constants import (
    ADJACENCIES_PATH,
    BAIRROS_UNIQUE_PATH,
    OUT_DIR,
    RECIFE_GLOBAL_PATH,
    MICRORREGIOES_PATH,
    EGO_BAIRRO_PATH,
    GRAUS_PATH,
)

class GraphAnalyzer:
    
    def __init__(self, adjacencies_path: str = ADJACENCIES_PATH, neighborhoods_path: str = BAIRROS_UNIQUE_PATH):
        self.adjacencies_path = adjacencies_path
        self.neighborhoods_path = neighborhoods_path
        self.graph: Optional[Graph] = None
        self.neighborhood_microregions: Dict[str, str] = {}
        
    def load_adjacencies(self, filepath: Optional[str] = None) -> pd.DataFrame:
        filepath = filepath or self.adjacencies_path
        df = pd.read_csv(filepath, encoding="utf-8")

        df["bairro_origem"] = df["bairro_origem"].apply(normalize_name)
        df["bairro_destino"] = df["bairro_destino"].apply(normalize_name)

        df = df.dropna(subset=["bairro_origem", "bairro_destino"])

        return df

    def load_neighborhoods_microregions(self, filepath: Optional[str] = None) -> Dict[str, str]:
        filepath = filepath or self.neighborhoods_path
        df = pd.read_csv(filepath, encoding="utf-8")
        df["bairro"] = df["bairro"].apply(normalize_name)
        df = df.drop_duplicates(subset=["bairro"], keep="first")

        mapping = dict(zip(df["bairro"], df["microrregiao"]))
        self.neighborhood_microregions = mapping

        return mapping

    def build_graph(self, adjacencies_df: Optional[pd.DataFrame] = None) -> Graph:
        if adjacencies_df is None:
            adjacencies_df = self.load_adjacencies()
            
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

        self.graph = graph
        return graph

    def compute_global_metrics(self, graph: Optional[Graph] = None) -> Dict:
        graph = graph or self.graph
        if graph is None:
            raise ValueError("Grafo não foi construído. Execute build_graph() primeiro.")
            
        metrics = graph.get_metrics()
        return metrics.to_dict()

    def compute_microregion_metrics(self, graph: Optional[Graph] = None, neighborhood_microregions: Optional[Dict[str, str]] = None) -> List[Dict]:
        graph = graph or self.graph
        if graph is None:
            raise ValueError("Grafo não foi construído. Execute build_graph() primeiro.")
            
        neighborhood_microregions = neighborhood_microregions or self.neighborhood_microregions
        if not neighborhood_microregions:
            self.load_neighborhoods_microregions()
            neighborhood_microregions = self.neighborhood_microregions
            
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

    def compute_ego_metrics(self, graph: Optional[Graph] = None) -> List[Dict]:
        graph = graph or self.graph
        if graph is None:
            raise ValueError("Grafo não foi construído. Execute build_graph() primeiro.")
            
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

        results.sort(key=lambda x: x["densidade_ego"], reverse=True)
        return results

    def ranking_degree(self, graph: Optional[Graph] = None) -> List[Dict]:
        graph = graph or self.graph
        if graph is None:
            raise ValueError("Grafo não foi construído. Execute build_graph() primeiro.")
            
        results = []
        for bairro in sorted(graph.get_vertices()):
            grau = graph.get_degree(bairro)
            results.append({"bairro": bairro, "grau": grau})

        results.sort(key=lambda x: x["grau"], reverse=True)
        return results

    def save_results(self, global_metrics: Dict, microregion_metrics: List[Dict], ego_metrics: List[Dict], rank_metrics: List[Dict], output_dir: str = OUT_DIR) -> None:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        global_path = Path(RECIFE_GLOBAL_PATH)
        with open(global_path, "w", encoding="utf-8") as f:
            json.dump(global_metrics, f, indent=2, ensure_ascii=False)

        microregion_path = Path(MICRORREGIOES_PATH)
        with open(microregion_path, "w", encoding="utf-8") as f:
            json.dump(microregion_metrics, f, indent=2, ensure_ascii=False)

        ego_path = Path(EGO_BAIRRO_PATH)
        with open(ego_path, "w", encoding="utf-8", newline="") as f:
            if ego_metrics:
                fieldnames = ["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(ego_metrics)

        ranking_path = Path(GRAUS_PATH)
        with open(ranking_path, "w", encoding="utf-8", newline="") as f:
            if rank_metrics:
                fieldnames = ["bairro", "grau"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rank_metrics)
                
        print(f"✓ Resultados salvos em {output_dir}/")

    def run_full_analysis(self) -> None:
        print("Carregando dados...")
        adjacencies_df = self.load_adjacencies()
        self.load_neighborhoods_microregions()

        print("Construindo grafo...")
        self.build_graph(adjacencies_df)

        print("Calculando métricas...")
        global_metrics = self.compute_global_metrics()
        microregion_metrics = self.compute_microregion_metrics()
        ego_metrics = self.compute_ego_metrics()
        ranking = self.ranking_degree()

        print("Salvando resultados...")
        self.save_results(global_metrics, microregion_metrics, ego_metrics, ranking)
        print("✓ Análise completa!")

def main():
    analyzer = GraphAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
