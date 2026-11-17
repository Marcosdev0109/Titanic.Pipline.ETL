"""
Pipeline ETL do Titanic: Extract, Transform, Load (+ geração de anúncios com IA).

Uso:
    python pipeline/etl.py                 # só ETL, sem IA
    GOOGLE_API_KEY=... python pipeline/etl.py --ia 20   # gera anúncios com o Gemini para 20 passageiros

A chave da API NUNCA fica no código: ela é lida da variável de ambiente GOOGLE_API_KEY.
Saída: docs/data/passageiros.json, site/data/estatisticas.json e site/data/anuncios.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "titanic.csv"
SAIDA = RAIZ / "docs" / "data"

PORTOS = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}
CLASSES = {1: "Primeira classe", 2: "Segunda classe", 3: "Terceira classe"}
TITULOS_PT = {
    "Mr": "Sr.", "Mrs": "Sra.", "Miss": "Srta.", "Master": "Menino",
    "Dr": "Dr.", "Rev": "Rev.", "Col": "Cel.", "Major": "Maj.", "Capt": "Cap.",
}


# ---------------------------------------------------------------- Extract
def extrair(caminho: Path = ENTRADA) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    print(f"[extract] {len(df)} passageiros lidos de {caminho.name}")
    return df


# ---------------------------------------------------------------- Transform
def titulo_do_nome(nome: str) -> str:
    m = re.search(r",\s*([^\.]+)\.", nome)
    t = m.group(1).strip() if m else "Outro"
    t = {"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs", "Lady": "Mrs", "the Countess": "Mrs",
         "Dona": "Mrs", "Sir": "Mr", "Don": "Mr", "Jonkheer": "Mr"}.get(t, t)
    return t if t in TITULOS_PT else "Outro"


def nome_legivel(nome: str) -> str:
    """'Braund, Mr. Owen Harris' -> 'Owen Harris Braund'. Mantém o nome de solteira entre parênteses."""
    sobrenome, resto = (nome.split(",", 1) + [""])[:2]
    resto = re.sub(r"^\s*[^\.]+\.\s*", "", resto).strip()
    m = re.search(r"\(([^)]+)\)", resto)
    if m:  # mulheres casadas: o nome dela aparece entre parênteses
        return f"{m.group(1).strip()} {sobrenome.strip()}".replace('"', "")
    return f"{resto} {sobrenome.strip()}".replace('"', "").strip()


def faixa_etaria(idade: float) -> str:
    if idade < 13: return "Criança"
    if idade < 18: return "Adolescente"
    if idade < 60: return "Adulto"
    return "Idoso"


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["titulo"] = df["Name"].map(titulo_do_nome)

    # Idade: 177 faltando. Preenche com a mediana do título (Menino ~4 anos, Sr. ~30) e marca como estimada.
    df["idade_estimada"] = df["Age"].isna()
    mediana = df.groupby("titulo")["Age"].transform("median")
    df["Age"] = df["Age"].fillna(mediana).fillna(df["Age"].median()).round(1)

    # Porto: 2 faltando. Preenche com o mais comum (Southampton).
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Convés: primeira letra da cabine; 687 sem cabine registrada.
    df["deck"] = df["Cabin"].fillna("").str[0].replace({"": None, "T": None})

    df["familia"] = df["SibSp"] + df["Parch"]
    df["sozinho"] = df["familia"] == 0
    df["faixa"] = df["Age"].map(faixa_etaria)
    df["nome"] = df["Name"].map(nome_legivel)
    print(f"[transform] idades estimadas: {int(df['idade_estimada'].sum())}, portos preenchidos: 2")
    return df


def estatisticas(df: pd.DataFrame) -> dict:
    def taxa(col):
        g = df.groupby(col)["Survived"].agg(["mean", "count"])
        return [{"grupo": str(k), "taxa": round(float(v["mean"]), 3), "total": int(v["count"])} for k, v in g.iterrows()]

    ordem_faixa = ["Criança", "Adolescente", "Adulto", "Idoso"]
    faixa = sorted(taxa("faixa"), key=lambda x: ordem_faixa.index(x["grupo"]))
    return {
        "total": int(len(df)),
        "sobreviventes": int(df["Survived"].sum()),
        "taxa_geral": round(float(df["Survived"].mean()), 3),
        "por_classe": [{**x, "grupo": CLASSES[int(x["grupo"])]} for x in taxa("Pclass")],
        "por_sexo": [{**x, "grupo": "Mulheres" if x["grupo"] == "female" else "Homens"} for x in taxa("Sex")],
        "por_faixa": faixa,
        "por_porto": [{**x, "grupo": PORTOS[x["grupo"]]} for x in taxa("Embarked")],
        "sozinho": [{**x, "grupo": "Sozinho" if x["grupo"] == "True" else "Com família"} for x in taxa("sozinho")],
    }


# ---------------------------------------------------------------- Geração com IA (opcional)
PROMPT = """Você é redator da equipe de marketing da White Star Line, em abril de 1912, dias antes da viagem inaugural do RMS Titanic.
Escreva um anúncio curto (até 70 palavras), em português, convidando este passageiro a embarcar.
Use os dados para personalizar o tom: classe, idade, se viaja sozinho ou com família e o porto de embarque.
Não mencione o naufrágio nem o destino do passageiro.

Dados: {dados}"""


def gerar_anuncios(df: pd.DataFrame, quantidade: int, existentes: dict) -> dict:
    chave = os.environ.get("GOOGLE_API_KEY")
    if not chave:
        print("[ia] GOOGLE_API_KEY não definida: pulando a geração de anúncios.")
        return existentes
    from google import genai  # importado só quando há chave

    cliente = genai.Client(api_key=chave)
    amostra = df[~df["PassengerId"].astype(str).isin(existentes)].sample(quantidade, random_state=42)
    for _, p in amostra.iterrows():
        dados = {"nome": p["nome"], "classe": CLASSES[p["Pclass"]], "idade": p["Age"],
                 "familia_a_bordo": int(p["familia"]), "porto": PORTOS[p["Embarked"]]}
        resp = cliente.models.generate_content(model="gemini-2.5-flash", contents=PROMPT.format(dados=json.dumps(dados, ensure_ascii=False)))
        existentes[str(p["PassengerId"])] = {"texto": resp.text.strip(), "modelo": "gemini-2.5-flash"}
        print(f"[ia] anúncio gerado para {p['nome']}")
        time.sleep(1)  # respeita o limite de requisições
    return existentes


# ---------------------------------------------------------------- Load
def carregar(df: pd.DataFrame, stats: dict, anuncios: dict) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    registros = [{
        "id": int(p["PassengerId"]), "nome": p["nome"], "titulo": TITULOS_PT.get(p["titulo"], ""),
        "sexo": "F" if p["Sex"] == "female" else "M", "idade": float(p["Age"]), "idade_estimada": bool(p["idade_estimada"]),
        "classe": int(p["Pclass"]), "tarifa": round(float(p["Fare"]), 2), "bilhete": p["Ticket"],
        "cabine": p["Cabin"] if isinstance(p["Cabin"], str) else None, "deck": p["deck"] if isinstance(p["deck"], str) else None,
        "porto": PORTOS[p["Embarked"]], "familia": int(p["familia"]), "sobreviveu": bool(p["Survived"]),
    } for _, p in df.iterrows()]
    (SAIDA / "passageiros.json").write_text(json.dumps(registros, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (SAIDA / "estatisticas.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDA / "anuncios.json").write_text(json.dumps(anuncios, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[load] {len(registros)} passageiros, {len(anuncios)} anúncios salvos em {SAIDA.relative_to(RAIZ)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ia", type=int, default=0, help="quantos anúncios novos gerar com o Gemini")
    args = ap.parse_args()

    df = transformar(extrair())
    stats = estatisticas(df)
    arq = SAIDA / "anuncios.json"
    anuncios = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    if args.ia:
        anuncios = gerar_anuncios(df, args.ia, anuncios)
    carregar(df, stats, anuncios)


if __name__ == "__main__":
    main()
