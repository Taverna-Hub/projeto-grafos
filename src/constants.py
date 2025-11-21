from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "out"
PART1_DIR = OUT_DIR / "1. Grafo dos Bairros do Recife"
PART2_DIR = OUT_DIR / "2. Dataset Maior e Comparação de Algoritmos"

ADJACENCIES_PATH = str(DATA_DIR / "adjacencias_bairros.csv")
ENDERECOS_PATH = str(DATA_DIR / "enderecos.csv")
BAIRROS_RECIFE_PATH = str(DATA_DIR / "bairros_recife.csv")
BAIRROS_UNIQUE_PATH = str(DATA_DIR / "bairros_unique.csv")

RECIFE_GLOBAL_PATH = str(PART1_DIR / "1.3 Métricas globais e por grupo" / "recife_global.json")
MICRORREGIOES_PATH = str(PART1_DIR / "1.3 Métricas globais e por grupo" / "microrregioes.json")
EGO_BAIRRO_PATH = str(PART1_DIR / "1.3 Métricas globais e por grupo" / "ego_bairro.csv")

GRAUS_PATH = str(PART1_DIR / "1.4 Graus e Rankings" / "graus.csv")

DISTANCIAS_ENDERECOS_PATH = str(PART1_DIR / "1.6 Distância entre endereços X e Y" / "distancias_enderecos.csv")
PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH = str(
    PART1_DIR / "1.6 Distância entre endereços X e Y" / "percurso_nova_descoberta_setubal.json"
)

PART1_Q7_DIR = PART1_DIR / "1.7 Transforme o percurso em árvore e mostre"

PART1_Q8_DIR = PART1_DIR / "1.8 Explorações e visualizações analíticas"

PART1_Q9_DIR = PART1_DIR / "1.9 Apresentação interativa do grafo"
