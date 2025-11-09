from typing import Optional
import pandas as pd

def normalize_name(name: str) -> Optional[str]:
    if pd.isna(name) or name is None:
        return None

    name = str(name).strip()
    return " ".join(name.title().split())