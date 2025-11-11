from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "out"
PART1_DIR = OUT_DIR / "first_part"
PART2_DIR = OUT_DIR / "second_part"

ADJACENCIES_PATH = str(DATA_DIR / "adjacencias_bairros.csv")
ENDERECOS_PATH = str(DATA_DIR / "enderecos.csv")
BAIRROS_RECIFE_PATH = str(DATA_DIR / "bairros_recife.csv")
BAIRROS_UNIQUE_PATH = str(DATA_DIR / "bairros_unique.csv")

DISTANCIAS_ENDERECOS_PATH = str(PART1_DIR / "distancias_enderecos.csv")
RECIFE_GLOBAL_PATH = str(PART1_DIR / "recife_global.json")
MICRORREGIOES_PATH = str(PART1_DIR / "microrregioes.json")
EGO_BAIRRO_PATH = str(PART1_DIR / "ego_bairro.csv")
GRAUS_PATH = str(PART1_DIR / "graus.csv")
PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH = str(PART1_DIR / "percurso_nova_descoberta_setubal.json")