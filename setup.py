#!/usr/bin/env python3
"""
Script de instalación simplificado para Recetario WhatsApp.
Configura el entorno usando Python 3.11 y Poetry.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, shell=True):
    """Ejecuta un comando y devuelve True si fue exitoso."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Configurando Recetario WhatsApp...")
    print("=" * 50)

    # Verificar Python 3.11
    print("🐍 Verificando Python 3.11...")
    success, stdout, stderr = run_command("py -3.11 --version")
    if not success:
        print("❌ Python 3.11 no encontrado")
        print("💡 Instala Python 3.11 desde: https://python.org/downloads/")
        return False

    python_version = stdout.strip()
    print(f"✅ {python_version}")

    # Verificar Poetry
    print("\n🔧 Verificando Poetry...")
    success, stdout, stderr = run_command("py -3.11 -m pip show poetry")
    if not success:
        print("📦 Instalando Poetry...")
        success, stdout, stderr = run_command("py -3.11 -m pip install poetry")
        if not success:
            print(f"❌ Error instalando Poetry: {stderr}")
            return False

    print("✅ Poetry instalado")

    # Configurar Poetry para usar Python 3.11
    print("\n⚙️ Configurando Poetry...")
    commands = [
        "py -3.11 -m poetry config virtualenvs.in-project true",
        "py -3.11 -m poetry config virtualenvs.prefer-active-python true",
        "py -3.11 -m poetry env remove --all python",
        "py -3.11 -m poetry install"
    ]

    for cmd in commands:
        print(f"   Ejecutando: {cmd}")
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"❌ Error: {stderr}")
            return False

    print("✅ Entorno virtual configurado")

    # Limpiar archivos innecesarios
    print("\n🧹 Limpiando archivos temporales...")
    temp_files = [".venv", "venv", "__pycache__", ".pytest_cache", "htmlcov", ".coverage"]
    for item in temp_files:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
            else:
                os.remove(item)

    print("✅ Limpieza completada")

    # Verificar instalación
    print("\n🧪 Verificando instalación...")
    success, stdout, stderr = run_command("py -3.11 -m poetry run python -c \"import streamlit, supabase, mistralai; print('✅ Todas las dependencias funcionan')\"")
    if not success:
        print(f"❌ Error en dependencias: {stderr}")
        return False

    print("\n" + "=" * 50)
    print("🎉 ¡Configuración completada exitosamente!")
    print("\nPara ejecutar la aplicación:")
    print("  python run_app.py")
    print("  o")
    print("  py -3.11 -m poetry run streamlit run app_streamlit.py")
    print("\nPara procesar un archivo de WhatsApp:")
    print("  py -3.11 -m poetry run python -m src.recetario_whatsapp.extractor --file samples/recipes_sample.txt")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
