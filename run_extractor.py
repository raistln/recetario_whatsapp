#!/usr/bin/env python3
"""
Script para ejecutar el extractor usando Poetry.
"""
import subprocess
import sys
import os

def run_extractor(file_path):
    """Ejecuta el extractor usando Poetry."""
    try:
        # Asegurar que estamos en el directorio correcto
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Comando usando Poetry
        cmd = [
            "poetry", "run", "python", "-m", "src.recetario_whatsapp.extractor",
            "--file", file_path
        ]

        print(f"Ejecutando: {' '.join(cmd)}")
        print(f"Directorio: {project_dir}")

        # Ejecutar en el directorio del proyecto
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Código de salida: {result.returncode}")

        return result.returncode == 0

    except Exception as e:
        print(f"Error ejecutando extractor: {e}")
        return False

def main():
    """Función principal."""
    if len(sys.argv) != 2:
        print("Uso: python run_extractor.py <ruta_al_archivo>")
        print("Ejemplo: python run_extractor.py samples/recipes_sample.txt")
        return False

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe")
        return False

    success = run_extractor(file_path)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
