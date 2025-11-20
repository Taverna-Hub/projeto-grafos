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

RECIFE_GLOBAL_PATH = str(PART1_DIR / "3" / "recife_global.json")
MICRORREGIOES_PATH = str(PART1_DIR / "3" / "microrregioes.json")
EGO_BAIRRO_PATH = str(PART1_DIR / "3" / "ego_bairro.csv")

GRAUS_PATH = str(PART1_DIR / "4" / "graus.csv")

DISTANCIAS_ENDERECOS_PATH = str(PART1_DIR / "6" / "distancias_enderecos.csv")
PERCURSO_NOVA_DESCOBERTA_SETUBAL_PATH = str(
    PART1_DIR / "6" / "percurso_nova_descoberta_setubal.json"
)

PART1_Q7_DIR = PART1_DIR / "7"

PART1_Q8_DIR = PART1_DIR / "8"

PART1_Q9_DIR = PART1_DIR / "9"
