#!/usr/bin/env python3
"""Herramienta de inspección rápida para detectar problemas en el Excel de recetas."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import shorten

import pandas as pd


def summarize_row(values: list[str]) -> str:
    """Devuelve un resumen compacto de las primeras columnas."""
    cleaned = [shorten(str(v), width=50, placeholder="…") if v is not None else "" for v in values]
    return " | ".join(cleaned)


def inspect_excel(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    print("🔍 Analizando Excel:", path)
    sheets = pd.read_excel(path, sheet_name=None, dtype=str)
    print(f"📄 Hojas detectadas: {', '.join(sheets.keys())}\n")

    for sheet_name, df in sheets.items():
        print(f"=== Hoja: {sheet_name} ===")
        df = df.fillna("")
        print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
        print("Nombre de columnas:")
        for idx, col in enumerate(df.columns):
            print(f"  {idx+1:>2}. '{col}'")

        print("\nPrimeras filas relevantes:")
        for idx, (_, row) in enumerate(df.head(10).iterrows(), start=1):
            resumen = summarize_row(row.tolist()[:4])
            print(f"  {idx:>2}: {resumen}")
        print("\n")

    print("✅ Inspección completada")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspecciona el Excel de recetas")
    parser.add_argument(
        "ruta_excel",
        type=Path,
        nargs="?",
        default=Path("Recetas húngaras.xlsx"),
        help="Ruta al archivo Excel (default: Recetas húngaras.xlsx)",
    )
    args = parser.parse_args()
    inspect_excel(args.ruta_excel)


if __name__ == "__main__":
    main()
