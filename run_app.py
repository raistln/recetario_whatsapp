#!/usr/bin/env python3
"""
Script simplificado para ejecutar la aplicación Streamlit del recetario.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Ejecuta la aplicación Streamlit."""
    print("🚀 Iniciando Recetario WhatsApp...")
    print("📱 La aplicación se abrirá en tu navegador")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Para detener la aplicación, presiona Ctrl+C")
    print("-" * 50)

    try:
        # Verificar que el archivo principal existe
        if not os.path.exists("app_streamlit.py"):
            print("❌ Error: app_streamlit.py no encontrado")
            return False

        # Ejecutar Streamlit directamente con Python 3.11
        cmd = [
            "py", "-3.11", "-m", "streamlit", "run", "app_streamlit.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ]

        result = subprocess.run(cmd)
        return result.returncode == 0

    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario")
        return True
    except FileNotFoundError:
        print("❌ Error: Streamlit no encontrado")
        print("💡 Ejecuta primero: python setup.py")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
