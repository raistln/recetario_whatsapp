#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar problemas de dependencias
"""

import sys
import subprocess
import os

def check_dependency(package_name):
    """Verifica si un paquete está instalado"""
    try:
        __import__(package_name)
        return True, f"✅ {package_name} está instalado"
    except ImportError:
        return False, f"❌ {package_name} NO está instalado"

def install_package(package_name):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True, f"✅ {package_name} instalado correctamente"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Error instalando {package_name}: {e}"

def main():
    print("🔍 DIAGNOSTICANDO PROBLEMAS DE DEPENDENCIAS")
    print("=" * 50)

    # Verificar Python y entorno
    print(f"🐍 Python: {sys.executable}")
    print(f"📦 Versión: {sys.version}")

    # Verificar dependencias críticas
    dependencies = [
        'pandas',
        'openpyxl',
        'streamlit',
        'supabase',
        'mistralai',
        'cloudinary'
    ]

    print("\n📋 VERIFICANDO DEPENDENCIAS:")
    missing_deps = []

    for dep in dependencies:
        installed, message = check_dependency(dep)
        print(f"  {message}")
        if not installed:
            missing_deps.append(dep)

    if missing_deps:
        print(f"\n⚠️  DEPENDENCIAS FALTANTES: {missing_deps}")
        print("\n🔧 INSTALANDO DEPENDENCIAS FALTANTES...")

        for dep in missing_deps:
            print(f"\n📦 Instalando {dep}...")
            success, message = install_package(dep)
            print(f"  {message}")

    # Verificar que pandas puede usar openpyxl
    print("\n🧪 VERIFICANDO PANDAS + OPENPYXL:")
    try:
        import pandas as pd
        print(f"✅ Pandas versión: {pd.__version__}")

        # Probar carga de Excel
        try:
            # Crear un archivo Excel de prueba
            test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            test_df.to_excel('test.xlsx', index=False)
            test_read = pd.read_excel('test.xlsx')
            os.remove('test.xlsx')  # Limpiar
            print("✅ Pandas puede leer/escribir Excel correctamente")
        except ImportError as e:
            print(f"❌ Error con Excel: {e}")
        except Exception as e:
            print(f"⚠️  Error inesperado: {e}")

    except ImportError:
        print("❌ Error importando pandas")

    print("\n🎯 RECOMENDACIONES:")
    print("1. Si usas Poetry (recomendado):")
    print("   poetry install")
    print("   poetry run streamlit run app_streamlit.py")

    print("\n2. Si usas el entorno virtual actual:")
    print(f"   pip install pandas openpyxl streamlit supabase mistralai cloudinary")
    print(f"   {sys.executable} -m streamlit run app_streamlit.py")

if __name__ == "__main__":
    main()
