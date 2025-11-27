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


def generate_html_report(report: dict, output_path: Path) -> None:
    timestamp_raw = report.get("timestamp", "N/A")
    if timestamp_raw != "N/A":
        try:
            dt = datetime.fromisoformat(timestamp_raw)
            timestamp_formatted = dt.strftime("%d/%m/%Y às %H:%M:%S")
        except:
            timestamp_formatted = timestamp_raw
    else:
        timestamp_formatted = timestamp_raw

    html_content = (
        """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Testes - Algoritmos de Grafos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            line-height: 1.6;
        }
        
        header {
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        
        nav {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .menu-item {
            position: relative;
            display: inline-block;
        }
        
        .menu-item > a {
            color: white !important;
            text-decoration: none;
            padding: 1rem;
            display: inline-block;
        }
        
        .menu-item:hover > a {
            background-color: #555;
        }
        
        .submenu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            background-color: #444;
            min-width: 300px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            z-index: 1;
        }
        
        .submenu a {
            color: white !important;
            text-decoration: none;
            padding: 12px 16px;
            display: block;
            text-align: left;
        }
        
        .submenu a:hover {
            background-color: #555;
        }
        
        .menu-item:hover .submenu {
            display: block;
        }
        
        .container {
            max-width: 1400px;
            margin: 20px auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .metadata {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #ddd;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .metadata-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #495057;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .metadata-item strong {
            color: #495057;
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .test-section {
            margin-bottom: 40px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
        }
        
        .test-header {
            padding: 20px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .test-header.bfs {
            background-color: #2c3e50;
        }
        
        .test-header.dfs {
            background-color: #34495e;
        }
        
        .test-header.dijkstra {
            background-color: #445566;
        }
        
        .test-header.bellman_ford {
            background-color: #546e7a;
        }
        
        .test-header h2 {
            font-size: 1.5em;
            margin: 0;
        }
        
        .status-badge {
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .status-success {
            background: #28a745;
        }
        
        .status-failed {
            background: #6c757d;
        }
        
        .test-description {
            background: #f8f9fa;
            padding: 15px 20px;
            font-style: italic;
            color: #666;
            border-left: 4px solid #6c757d;
        }
        
        .test-body {
            padding: 20px;
            background: white;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        thead {
            background-color: #495057;
            color: white;
        }
        
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tbody tr {
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        tbody tr:nth-child(even) {
            background-color: #fafafa;
        }
        
        tbody tr:nth-child(even):hover {
            background-color: #f0f0f0;
        }
        
        .path-cell {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #495057;
            max-width: 400px;
            word-break: break-word;
        }
        
        .number-cell {
            font-weight: 600;
            color: #495057;
        }
        
        .error-message {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .cycle-detected {
            background: #fff8e1;
            border: 2px solid #ffa726;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .cycle-detected::before {
            content: "⚠️";
            font-size: 2em;
        }
        
        .cycle-info {
            flex: 1;
        }
        
        .cycle-info strong {
            color: #e65100;
            font-size: 1.1em;
        }
        
        .negative-cycle {
            background: #ffebee;
            border: 2px solid #e57373;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .negative-cycle::before {
            content: "🔴";
            font-size: 2em;
        }
        
        .summary {
            background-color: #495057;
            color: white;
            padding: 30px;
            margin-top: 30px;
            border-radius: 8px;
            text-align: center;
        }
        
        .summary h2 {
            margin-bottom: 20px;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-box {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .stat-box .number {
            font-size: 3em;
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
        }
        
        .stat-box .label {
            font-size: 1.1em;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            margin-top: 30px;
            border-radius: 8px;
        }
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
                    <a href="../2. Dataset Maior e Comparação de Algoritmos/bitcoin_degree_distribution.html">Distribuição de Graus</a>
                    <a href="../2. Dataset Maior e Comparação de Algoritmos/bitcoin_distance_heatmap.html">Mapa de Distâncias</a>
                    <a href="../2. Dataset Maior e Comparação de Algoritmos/bitcoin_graph_sample.html">Amostra do Grafo</a>
                    <a href="../2. Dataset Maior e Comparação de Algoritmos/report.html">Relatório de Testes</a>
                </div>
            </div>
        </nav>
    </header>
    
    <div class="container">
        <h1>Relatório de Testes - Algoritmos de Grafos</h1>
        <p class="subtitle">Análise Completa de Algoritmos de Busca e Caminho Mínimo</p>
        
        <div class="metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <strong>⏰ Timestamp</strong>
                    <span>"""
        + timestamp_formatted
        + """</span>
                </div>
                <div class="metadata-item">
                    <strong>📁 Dataset</strong>
                    <span>"""
        + report.get("dataset", "N/A")
        + """</span>
                </div>
                <div class="metadata-item">
                    <strong>🧪 Total de Testes</strong>
                    <span>"""
        + str(len(report.get("tests", {})))
        + """ algoritmos testados</span>
                </div>
            </div>
        </div>
"""
    )

    tests = report.get("tests", {})

    if "bfs" in tests:
        html_content += generate_bfs_section(tests["bfs"])

    if "dfs" in tests:
        html_content += generate_dfs_section(tests["dfs"])

    if "dijkstra" in tests:
        html_content += generate_dijkstra_section(tests["dijkstra"])

    if "bellman_ford" in tests:
        html_content += generate_bellman_ford_section(tests["bellman_ford"])

    html_content += generate_summary(tests)

    html_content += (
        """
        
        <footer>
            <p>Gerado automaticamente em """
        + datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        + """</p>
            <p>Projeto de Grafos - Análise de Algoritmos</p>
        </footer>
    </div>
</body>
</html>"""
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_bfs_section(bfs_data: dict) -> str:
    status = bfs_data.get("status", "unknown")
    status_class = (
        "status-success" if status in ["success", "sucesso"] else "status-failed"
    )

    section = f"""
            <div class="test-section">
                <div class="test-header bfs">
                    <h2>BFS - Breadth-First Search</h2>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <div class="test-description">
                    {bfs_data.get('description', '')}
                </div>
                <div class="test-body">
"""

    if status in ["success", "sucesso"] and "results" in bfs_data:
        results = bfs_data["results"]
        section += """
                    <table>
                        <thead>
                            <tr>
                                <th>Origem</th>
                                <th>Nós Alcançáveis</th>
                                <th>Total de Nós</th>
                                <th>Camadas</th>
                                <th>Tempo (s)</th>
                                <th>Memória Pico (MB)</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for result in results:
            time_str = (
                f"{result.get('time_seconds', 0):.6f}"
                if "time_seconds" in result
                else "N/A"
            )
            memory_str = (
                f"{result.get('peak_memory_mb', 0):.2f}"
                if "peak_memory_mb" in result
                else "N/A"
            )

            section += f"""
                            <tr>
                                <td class="number-cell">{result.get('source', 'N/A')}</td>
                                <td class="number-cell">{result.get('reachable_nodes', 0)}</td>
                                <td class="number-cell">{result.get('total_nodes', 0)}</td>
                                <td class="number-cell">{result.get('layers', 0)}</td>
                                <td class="number-cell">{time_str}</td>
                                <td class="number-cell">{memory_str}</td>
                            </tr>
"""

        section += """
                        </tbody>
                    </table>
"""
    else:
        section += f"""
                    <div class="error-message">
                        <strong>Erro:</strong> {bfs_data.get('error', 'Erro desconhecido')}
                    </div>
"""

    section += """
                </div>
            </div>
"""
    return section


def generate_dfs_section(dfs_data: dict) -> str:
    status = dfs_data.get("status", "unknown")
    status_class = (
        "status-success" if status in ["success", "sucesso"] else "status-failed"
    )

    section = f"""
            <div class="test-section">
                <div class="test-header dfs">
                    <h2>DFS - Depth-First Search</h2>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <div class="test-description">
                    {dfs_data.get('description', '')}
                </div>
                <div class="test-body">
"""

    if status in ["success", "sucesso"] and "results" in dfs_data:
        results = dfs_data["results"]
        section += """
                    <table>
                        <thead>
                            <tr>
                                <th>Origem</th>
                                <th>Nós Visitados</th>
                                <th>Total de Nós</th>
                                <th>Ciclos?</th>
                                <th>Arestas de Retorno</th>
                                <th>Tempo (s)</th>
                                <th>Memória Pico (MB)</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for result in results:
            has_cycles = result.get("has_cycles", False)
            cycle_badge = "Sim" if has_cycles else "❌ Não"
            time_str = (
                f"{result.get('time_seconds', 0):.6f}"
                if "time_seconds" in result
                else "N/A"
            )
            memory_str = (
                f"{result.get('peak_memory_mb', 0):.2f}"
                if "peak_memory_mb" in result
                else "N/A"
            )

            section += f"""
                            <tr>
                                <td class="number-cell">{result.get('source', 'N/A')}</td>
                                <td class="number-cell">{result.get('visited_nodes', 0)}</td>
                                <td class="number-cell">{result.get('total_nodes', 0)}</td>
                                <td><strong>{cycle_badge}</strong></td>
                                <td class="number-cell">{result.get('back_edges', 0)}</td>
                                <td class="number-cell">{time_str}</td>
                                <td class="number-cell">{memory_str}</td>
                            </tr>
"""

        section += """
                        </tbody>
                    </table>
"""

        if any(r.get("has_cycles", False) for r in results):
            section += """
                    <div class="cycle-detected">
                        <div class="cycle-info">
                            <strong>Ciclo Detectado no Grafo!</strong>
                            <p>O algoritmo DFS identificou pelo menos um ciclo no grafo analisado.</p>
                        </div>
                    </div>
"""
    else:
        section += f"""
                    <div class="error-message">
                        <strong>Erro:</strong> {dfs_data.get('error', 'Erro desconhecido')}
                    </div>
"""

    section += """
                </div>
            </div>
"""
    return section


def generate_dijkstra_section(dijkstra_data: dict) -> str:
    status = dijkstra_data.get("status", "unknown")
    status_class = (
        "status-success" if status in ["success", "sucesso"] else "status-failed"
    )

    section = f"""
            <div class="test-section">
                <div class="test-header dijkstra">
                    <h2>Dijkstra - Caminho Mínimo</h2>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <div class="test-description">
                    {dijkstra_data.get('description', '')}
                </div>
                <div class="test-body">
"""

    if status in ["success", "sucesso"] and "results" in dijkstra_data:
        results = dijkstra_data["results"]
        section += """
                    <table>
                        <thead>
                            <tr>
                                <th>Origem</th>
                                <th>Destino</th>
                                <th>Peso</th>
                                <th>Comprimento do Caminho</th>
                                <th>Encontrado?</th>
                                <th>Tempo (s)</th>
                                <th>Memória Pico (MB)</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for result in results:
            weight = result.get("weight", float("inf"))
            weight_str = f"{weight:.2f}" if weight != float("inf") else "∞"
            found = result.get("found", False)
            found_badge = "Sim" if found else "❌ Não"
            time_str = (
                f"{result.get('time_seconds', 0):.6f}"
                if "time_seconds" in result
                else "N/A"
            )
            memory_str = (
                f"{result.get('peak_memory_mb', 0):.2f}"
                if "peak_memory_mb" in result
                else "N/A"
            )

            section += f"""
                            <tr>
                                <td class="number-cell">{result.get('origin', 'N/A')}</td>
                                <td class="number-cell">{result.get('destination', 'N/A')}</td>
                                <td class="number-cell">{weight_str}</td>
                                <td class="number-cell">{result.get('path_length', 0)}</td>
                                <td><strong>{found_badge}</strong></td>
                                <td class="number-cell">{time_str}</td>
                                <td class="number-cell">{memory_str}</td>
                            </tr>
"""

        section += """
                        </tbody>
                    </table>
"""
    else:
        section += f"""
                    <div class="error-message">
                        <strong>Erro:</strong> {dijkstra_data.get('error', 'Erro desconhecido')}
                    </div>
"""

    section += """
                </div>
            </div>
"""
    return section


def generate_bellman_ford_section(bellman_data: dict) -> str:
    status = bellman_data.get("status", "unknown")
    status_class = (
        "status-success" if status in ["success", "sucesso"] else "status-failed"
    )

    section = f"""
            <div class="test-section">
                <div class="test-header bellman_ford">
                    <h2>Bellman-Ford - Pesos Negativos</h2>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <div class="test-description">
                    {bellman_data.get('description', '')}
                </div>
                <div class="test-body">
"""

    if status in ["success", "sucesso"] and "results" in bellman_data:
        results = bellman_data["results"]
        section += """
                    <table>
                        <thead>
                            <tr>
                                <th>Teste</th>
                                <th>Origem</th>
                                <th>Total de Nós</th>
                                <th>Nós Alcançáveis</th>
                                <th>Ciclo Negativo?</th>
                                <th>Tempo (s)</th>
                                <th>Memória (KB/MB)</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for result in results:
            negative_cycle = result.get("negative_cycle", False)
            cycle_badge = "Sim" if negative_cycle else "Não"
            time_str = (
                f"{result.get('time_seconds', 0):.6f}"
                if "time_seconds" in result
                else "N/A"
            )

            if "peak_memory_mb" in result:
                memory_str = f"{result.get('peak_memory_mb', 0):.2f} MB"
            elif "peak_memory_kb" in result:
                memory_str = f"{result.get('peak_memory_kb', 0):.2f} KB"
            else:
                memory_str = "N/A"

            reachable_nodes = result.get("reachable_nodes", "N/A")
            test_name = result.get("test", "N/A").replace("_", " ").title()

            translations = {
                "Positive Weights": "Pesos Positivos",
                "Negative Weights No Cycle": "Pesos Negativos sem Ciclo",
                "Negative Cycle": "Ciclo Negativo",
            }
            test_name = translations.get(test_name, test_name)

            section += f"""
                            <tr>
                                <td>{test_name}</td>
                                <td class="number-cell">{result.get('source', 'N/A')}</td>
                                <td class="number-cell">{result.get('total_nodes', 0)}</td>
                                <td class="number-cell">{reachable_nodes}</td>
                                <td><strong>{cycle_badge}</strong></td>
                                <td class="number-cell">{time_str}</td>
                                <td class="number-cell">{memory_str}</td>
                            </tr>
"""

        section += """
                        </tbody>
                    </table>
"""

        if any(r.get("negative_cycle", False) for r in results):
            section += """
                    <div class="negative-cycle">
                        <div class="cycle-info">
                            <strong>Ciclo Negativo Detectado!</strong>
                            <p>O algoritmo Bellman-Ford identificou um ciclo negativo no grafo. Isso significa que não há caminho mínimo bem definido para alguns pares de vértices.</p>
                        </div>
                    </div>
"""
    else:
        section += f"""
                    <div class="error-message">
                        <strong>Erro:</strong> {bellman_data.get('error', 'Erro desconhecido')}
                    </div>
"""

    section += """
                </div>
            </div>
"""
    return section


def generate_summary(tests: dict) -> str:
    total_tests = len(tests)
    successful_tests = sum(
        1 for test in tests.values() if test.get("status") in ["success", "sucesso"]
    )
    failed_tests = total_tests - successful_tests

    total_executions = 0
    for test_name, test_data in tests.items():
        if test_data.get("status") in ["success", "sucesso"] and "results" in test_data:
            total_executions += len(test_data["results"])

    summary = f"""
            <div class="summary">
                <h2>Resumo da Execução</h2>
                <div class="summary-stats">
                    <div class="stat-box">
                        <span class="number">{total_tests}</span>
                        <span class="label">Algoritmos Testados</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{successful_tests}</span>
                        <span class="label">Testes Bem-Sucedidos</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{failed_tests}</span>
                        <span class="label">Testes Falhados</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{total_executions}</span>
                        <span class="label">Total de Execuções</span>
                    </div>
                </div>
            </div>
"""
    return summary


def main():

    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset": "bitcoin_alpha.csv",
        "tests": {},
    }

    try:
        bfs_results = test_bfs_bitcoin_alpha()
        report["tests"]["bfs"] = {
            "description": "BFS a partir de ≥3 fontes distintas com análise de camadas",
            "status": "sucesso",
            "results": bfs_results,
        }
    except Exception as e:
        report["tests"]["bfs"] = {"status": "falhou", "error": str(e)}

    try:
        dfs_results = test_dfs_bitcoin_alpha()
        report["tests"]["dfs"] = {
            "description": "DFS a partir de ≥3 fontes distintas com detecção de ciclos",
            "status": "sucesso",
            "results": dfs_results,
        }
    except Exception as e:
        report["tests"]["dfs"] = {"status": "falhou", "error": str(e)}

    try:
        dijkstra_results = test_dijkstra_bitcoin_alpha()
        report["tests"]["dijkstra"] = {
            "description": "Dijkstra com ≥5 pares origem-destino (pesos ≥ 0)",
            "status": "sucesso",
            "results": dijkstra_results,
        }
    except Exception as e:
        report["tests"]["dijkstra"] = {"status": "falhou", "error": str(e)}

    try:
        bellman_results = test_bellman_ford_bitcoin_alpha()
        report["tests"]["bellman_ford"] = {
            "description": "Bellman-Ford com pesos positivos, negativos e ciclo negativo",
            "status": "sucesso",
            "results": bellman_results,
        }
    except Exception as e:
        report["tests"]["bellman_ford"] = {"status": "falhou", "error": str(e)}

    output_dir = Path(PART2_DIR)
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "report.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    html_path = output_dir / "report.html"
    generate_html_report(report, html_path)

    return report


if __name__ == "__main__":
    main()
