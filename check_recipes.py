#!/usr/bin/env python3
"""
Script para verificar las recetas guardadas usando Poetry.
"""
import subprocess
import sys
import os

def check_recipes():
    """Verifica las recetas guardadas."""
    try:
        # Asegurar que estamos en el directorio correcto
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Comando usando Poetry para ejecutar un script que verifica las recetas
        check_script = '''
import sys
sys.path.insert(0, "src")
from dotenv import load_dotenv
load_dotenv()
from recetario_whatsapp.supabase_utils import SupabaseManager
sm = SupabaseManager()
recetas = sm.obtener_recetas()
print(f"Total recetas: {len(recetas)}")
if recetas:
    for i, r in enumerate(recetas, 1):
        print(f"{i}. {r[\"nombre_receta\"]} por {r[\"creador\"]}")
        print(f"   🥘 {r[\"ingredientes\"]}")
        print(f"   👨‍🍳 {r.get(\"pasos_preparacion\", \"Sin pasos\")}")
        print()
else:
    print("No hay recetas guardadas")
'''

        cmd = ["poetry", "run", "python", "-c", check_script]

        print("Verificando recetas guardadas...")
        print(f"Comando: {' '.join(cmd[:3])} -c [script]")

        # Ejecutar en el directorio del proyecto
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

        print("SALIDA:")
        print(result.stdout)
        if result.stderr:
            print("ERRORES:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error verificando recetas: {e}")
        return False

def main():
    """Función principal."""
    success = check_recipes()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
