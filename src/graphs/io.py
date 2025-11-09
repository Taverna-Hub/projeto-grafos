import pandas as pd
from pathlib import Path
from typing import Optional
from utils.normalize import normalize_name
from constants import BAIRROS_RECIFE_PATH, BAIRROS_UNIQUE_PATH

class CSVLoader:
    
    def __init__(self, bairros_path: str = BAIRROS_RECIFE_PATH, output_path: str = BAIRROS_UNIQUE_PATH):
        self.bairros_path = bairros_path
        self.output_path = output_path
        self.df: Optional[pd.DataFrame] = None
    
    def load_bairros(self, filepath: Optional[str] = None) -> pd.DataFrame:
        filepath = filepath or self.bairros_path
        self.df = pd.read_csv(filepath, dtype=str, encoding="utf-8")
        return self.df
    
    def process_microregions(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        if df is None:
            if self.df is None:
                self.load_bairros()
            df = self.df
        
        melted = df.melt(value_name="bairro", var_name="microrregiao")[
            ["bairro", "microrregiao"]
        ]
        melted = melted.dropna(subset=["bairro"])
        melted["bairro"] = melted["bairro"].apply(normalize_name)
        melted["bairro"] = melted["bairro"].replace({"Setúbal": "Boa Viagem (Setúbal)"})

        bairros_unique = melted.drop_duplicates().reset_index(drop=True)
        return bairros_unique
    
    def save_unique_neighborhoods(self, output_path: Optional[str] = None) -> None:
        output_path = output_path or self.output_path
        bairros_unique = self.process_microregions()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        bairros_unique.to_csv(output_path, index=False, encoding="utf-8")
        print(f"✓ Bairros únicos salvos em {output_path}")
    
    def run(self) -> None:
        print("Carregando dados de bairros...")
        self.load_bairros()
        print("Processando microrregiões...")
        self.save_unique_neighborhoods()
        print("✓ Processamento completo!")

def main():

    loader = CSVLoader()
    loader.run()

if __name__ == "__main__":
    main()
