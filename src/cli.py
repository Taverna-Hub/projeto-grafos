import sys
import argparse
from pathlib import Path
from solve import GraphAnalyzer
from graphs.io import CSVLoader
from graphs.algorithms import Algorithms
from viz import GraphVisualizer

from constants import (
    ADJACENCIES_PATH,
    BAIRROS_UNIQUE_PATH,
    ENDERECOS_PATH,
    RECIFE_GLOBAL_PATH,
    MICRORREGIOES_PATH,
    EGO_BAIRRO_PATH,
    GRAUS_PATH,
    DISTANCIAS_ENDERECOS_PATH,
    PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH,
)

class GraphCLI:
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:

        parser = argparse.ArgumentParser(
            description="Análise de Grafos - Bairros do Recife",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemplos de uso:
  %(prog)s analyze                      # Executa análise completa do grafo -> ego_bairro.csv, graus.csv, microrregioes.json e recife_global.json
  %(prog)s path "Boa Viagem" "Graças"   # Encontra caminho entre bairros
  %(prog)s process                      # Processa dados de entrada -> bairros_unique.csv
  %(prog)s distances                    # Calcula distâncias em lote -> distancias_enderecos.csv e percurso_nova_descoberta_setubal.json
  %(prog)s visualize [json_file]        # Gera visualização de árvore de percurso a partir de JSON
  %(prog)s info --type global           # Mostra métricas globais
  %(prog)s info --type microregions     # Mostra métricas por microrregião
  %(prog)s info --type ego              # Mostra ranking por densidade ego
  %(prog)s info --type degree           # Mostra ranking por grau
                                """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
        
        # Comando: analyze
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='Executa análise completa do grafo -> ego_bairro.csv, graus.csv, microrregioes.json e recife_global.json'
        )
        
        # Comando: path
        path_parser = subparsers.add_parser(
            'path',
            help='Encontra caminho entre dois bairros usando Dijkstra'
        )
        path_parser.add_argument(
            'start',
            help='Bairro de origem'
        )
        path_parser.add_argument(
            'end',
            help='Bairro de destino'
        )
        
        # Comando: process
        process_parser = subparsers.add_parser(
            'process',
            help='Processa dados de entrada -> bairros_unique.csv'
        )
        
        # Comando: distances
        distances_parser = subparsers.add_parser(
            'distances',
            help='Calcula distâncias em lote para pares de endereços -> distancias_enderecos.csv e percurso_nova_descoberta_setubal.json'
        )
        
        # Comando: visualize
        visualize_parser = subparsers.add_parser(
            'visualize',
            help='Gera visualização de árvore de percurso a partir de arquivo JSON'
        )
        visualize_parser.add_argument(
            'json_file',
            nargs='?',
            default=str(PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH),
            help=f'Caminho para o arquivo JSON com dados do percurso (padrão: {PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH})'
        )
        
        # Comando: info
        info_parser = subparsers.add_parser(
            'info',
            help='Exibe informações sobre os resultados das análises'
        )
        info_parser.add_argument(
            '--type',
            choices=['global', 'microregions', 'ego', 'degree'],
            default='global',
            help='Tipo de informação a exibir (padrão: global)'
        )
        
        return parser
    
    def cmd_analyze(self, args) -> int:
        try:
            print("=" * 60)
            print("ANÁLISE COMPLETA DO GRAFO DE BAIRROS")
            print("=" * 60)
            
            analyzer = GraphAnalyzer()
            analyzer.run_full_analysis()
            
            print("\n" + "=" * 60)
            print("Resultados salvos:")
            print(f"  • Métricas globais: {RECIFE_GLOBAL_PATH}")
            print(f"  • Microrregiões: {MICRORREGIOES_PATH}")
            print(f"  • Redes ego: {EGO_BAIRRO_PATH}")
            print(f"  • Ranking por grau: {GRAUS_PATH}")
            print("=" * 60)
            
            return 0
        except Exception as e:
            print(f"❌ Erro ao executar análise: {e}", file=sys.stderr)
            return 1
    
    def cmd_path(self, args) -> int:
        try:
            print("=" * 60)
            print(f"BUSCA DE CAMINHO: {args.start} → {args.end}")
            print(f"Algoritmo: DIJKSTRA")
            print("=" * 60)
            
            algorithms = Algorithms()
            print("\nCarregando grafo...")
            algorithms.load_graph_from_csv(ADJACENCIES_PATH)
            
            print("Executando Dijkstra...\n")
            cost, path = algorithms.dijkstra(args.start, args.end)
            print(f"Custo total: {cost}")
            print(f"Caminho: {path}")

            if args.start == "Nova Descoberta" and args.end == "Boa Viagem":
                import json
                result = {
                    "origem": args.start,
                    "destino": args.end,
                    "custo": cost,
                    "caminho": path
                }
                
                Path(PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH).parent.mkdir(parents=True, exist_ok=True)
                with open(PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"\n✓ Resultado salvo em: {PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH}")
            
            print("=" * 60)
            return 0
            
        except Exception as e:
            print(f"❌ Erro ao buscar caminho: {e}", file=sys.stderr)
            return 1
    
    def cmd_process(self, args) -> int:
        try:
            print("=" * 60)
            print("PROCESSAMENTO DE DADOS")
            print("=" * 60)
            
            loader = CSVLoader()
            loader.run()
            
            print("=" * 60)
            return 0
            
        except Exception as e:
            print(f"❌ Erro ao processar dados: {e}", file=sys.stderr)
            return 1
    
    def cmd_distances(self, args) -> int:
        try:
            print("=" * 60)
            print("CÁLCULO DE DISTÂNCIAS EM LOTE")
            print("=" * 60)
            
            algorithms = Algorithms()
            print("\nCarregando grafo...")
            algorithms.load_graph_from_csv(ADJACENCIES_PATH)
            
            print("Calculando distâncias...\n")
            algorithms.compute_distances_batch()
            
            print(f"\n✓ Resultados salvos em: {DISTANCIAS_ENDERECOS_PATH}")
            print("=" * 60)
            return 0
            
        except Exception as e:
            print(f"❌ Erro ao calcular distâncias: {e}", file=sys.stderr)
            return 1
    
    def cmd_visualize(self, args) -> int:
        try:
            import json
            
            print("=" * 60)
            print("GERAÇÃO DE VISUALIZAÇÃO DE ÁRVORE DE PERCURSO")
            print("=" * 60)
            
            json_path = Path(args.json_file)
            
            if not json_path.exists():
                print(f"Erro: Arquivo {json_path} não encontrado!")
                print("\n Dica: Execute primeiro um dos comandos:")
                return 1
            
            print(f"\nCarregando dados de: {json_path}")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            visualizer = GraphVisualizer(output_dir="out")
            
            visualizer.viz_path_tree(
                caminho=data["caminho"],
                origem=data["origem"],
                destino=data["destino"],
                custo=data["custo"]
            )
            
            print("\nÁrvore de caminho gerada com sucesso!")
            print("=" * 60)
            return 0
            
        except Exception as e:
            print(f"Erro ao gerar visualização: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def cmd_info(self, args) -> int:
        try:
            import json
            import csv
            
            print("=" * 60)
            print(f"INFORMAÇÕES: {args.type.upper()}")
            print("=" * 60)
            
            if args.type == 'global':
                if not Path(RECIFE_GLOBAL_PATH).exists():
                    print("❌ Arquivo de métricas globais não encontrado.")
                    print("   Execute 'python src/cli.py analyze' primeiro.")
                    return 1
                
                with open(RECIFE_GLOBAL_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\nMétricas Globais do Grafo:")
                print(f"  • Ordem (vértices): {data.get('ordem', 'N/A')}")
                print(f"  • Tamanho (arestas): {data.get('tamanho', 'N/A')}")
                print(f"  • Densidade: {data.get('densidade', 'N/A'):.4f}")
            
            elif args.type == 'microregions':
                if not Path(MICRORREGIOES_PATH).exists():
                    print("❌ Arquivo de microrregiões não encontrado.")
                    print("   Execute 'python src/cli.py analyze' primeiro.")
                    return 1
                
                with open(MICRORREGIOES_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\nMicrorregiões ({len(data)} encontradas):")
                for item in data[:5]: 
                    print(f"\n  {item['microrregiao']}:")
                    print(f"    • Bairros: {len(item['bairros'])}")
                    print(f"    • Ordem: {item['ordem']}")
                    print(f"    • Tamanho: {item['tamanho']}")
                    print(f"    • Densidade: {item['densidade']:.4f}")
                
                if len(data) > 5:
                    print(f"\n  ... e mais {len(data) - 5} microrregiões")
            
            elif args.type == 'ego':
                if not Path(EGO_BAIRRO_PATH).exists():
                    print("❌ Arquivo de redes ego não encontrado.")
                    print("   Execute 'python src/cli.py analyze' primeiro.")
                    return 1
                
                with open(EGO_BAIRRO_PATH, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                
                print(f"\nTop 10 Bairros por Densidade Ego:")
                for i, item in enumerate(data[:10], 1):
                    print(f"  {i}. {item['bairro']}")
                    print(f"     Grau: {item['grau']}, Densidade ego: {float(item['densidade_ego']):.4f}")
            
            elif args.type == 'degree':
                if not Path(GRAUS_PATH).exists():
                    print("❌ Arquivo de ranking por grau não encontrado.")
                    print("   Execute 'python src/cli.py analyze' primeiro.")
                    return 1
                
                with open(GRAUS_PATH, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                
                print(f"\nTop 10 Bairros por Grau:")
                for i, item in enumerate(data[:10], 1):
                    print(f"  {i}. {item['bairro']}: {item['grau']} conexões")
            
            print("\n" + "=" * 60)
            return 0
            
        except Exception as e:
            print(f"❌ Erro ao exibir informações: {e}", file=sys.stderr)
            return 1
    
    def run(self, argv=None) -> int:
        args = self.parser.parse_args(argv)
        
        if not args.command:
            self.parser.print_help()
            return 1

        command_map = {
            'analyze': self.cmd_analyze,
            'path': self.cmd_path,
            'process': self.cmd_process,
            'distances': self.cmd_distances,
            'visualize': self.cmd_visualize,
            'info': self.cmd_info
        }
        
        command_func = command_map.get(args.command)
        if command_func:
            return command_func(args)
        else:
            print(f"❌ Comando desconhecido: {args.command}", file=sys.stderr)
            return 1

def main():

    cli = GraphCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
