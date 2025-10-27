#!/usr/bin/env python3
"""Lista imágenes embebidas en un archivo Excel."""
from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import load_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspecciona imágenes embebidas en un Excel")
    parser.add_argument(
        "ruta_excel",
        type=Path,
        nargs="?",
        default=Path("Recetas húngaras.xlsx"),
        help="Ruta al archivo Excel (default: Recetas húngaras.xlsx)",
    )
    args = parser.parse_args()

    if not args.ruta_excel.exists():
        print(f"❌ No se encontró el archivo: {args.ruta_excel}")
        return

    wb = load_workbook(args.ruta_excel)
    print(f"📄 Archivo: {args.ruta_excel}")

    for ws in wb.worksheets:
        imagenes = getattr(ws, "_images", [])
        print(f"Hoja '{ws.title}': {len(imagenes)} imágenes")
        for idx, img in enumerate(imagenes, start=1):
            print(
                f"  {idx}. formato={getattr(img, 'format', 'desconocido')} "
                f"anchor={getattr(img.anchor, 'coord', None)} size={getattr(img, 'width', '?')}x{getattr(img, 'height', '?')}"
            )


if __name__ == "__main__":
    main()
