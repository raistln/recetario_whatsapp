#!/usr/bin/env python3
"""Procesa un Excel de recetas usando el extractor y muestra un resumen."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Asegurar que src esté en el path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))
from dotenv import load_dotenv
from recetario_whatsapp.extractor import WhatsAppExtractor


def main() -> None:
    parser = argparse.ArgumentParser(description="Procesa un archivo Excel de recetas")
    parser.add_argument(
        "ruta_excel",
        type=Path,
        nargs="?",
        default=Path("Recetas húngaras.xlsx"),
        help="Ruta al archivo Excel (default: Recetas húngaras.xlsx)",
    )
    args = parser.parse_args()

    # Cargar variables de entorno desde .env
    load_dotenv()

    extractor = WhatsAppExtractor()
    resultado = extractor.procesar_archivo(str(args.ruta_excel))

    print("=== RESUMEN ===")
    for clave, valor in resultado.items():
        print(f"{clave}: {valor}")

    if resultado.get("error"):
        exit(1)


if __name__ == "__main__":
    main()
