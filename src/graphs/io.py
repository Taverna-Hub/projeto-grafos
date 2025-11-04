import pandas as pd


def normalize_name(name):
    if pd.isna(name):
        return name

    name = str(name).strip()

    return " ".join(name.title().split())


df = pd.read_csv("data/bairros_recife.csv", dtype=str, encoding="utf-8")

melted = df.melt(value_name="bairro", var_name="microrregiao")[
    ["bairro", "microrregiao"]
]
melted = melted.dropna(subset=["bairro"])
melted["bairro"] = melted["bairro"].apply(normalize_name)
melted["bairro"] = melted["bairro"].replace({"Setúbal": "Boa Viagem (Setúbal)"})

bairros_unique = melted.drop_duplicates().reset_index(drop=True)
bairros_unique.to_csv("data/bairros_unique.csv", index=False)
