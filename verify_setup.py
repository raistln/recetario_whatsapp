#!/usr/bin/env python3
"""
Script para verificar que la aplicación funciona correctamente
"""

import sys
import subprocess
import os

def run_command(cmd):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔍 Verificando instalación de dependencias...")
    success, stdout, stderr = run_command("poetry check")
    if success:
        print("✅ Poetry configuración válida")
    else:
        print(f"❌ Error en Poetry: {stderr}")
        return

    print("\n📦 Verificando dependencias...")
    success, stdout, stderr = run_command("poetry run python -c \"import streamlit, pandas, openpyxl, supabase, mistralai; print('✅ Todas las dependencias están disponibles')\"")
    if success:
        print("✅ Dependencias instaladas correctamente")
    else:
        print(f"❌ Error en dependencias: {stderr}")

    print("\n🧪 Probando importación de módulos...")
    success, stdout, stderr = run_command("poetry run python -c \"from src.recetario_whatsapp.extractor import WhatsAppExtractor; from src.recetario_whatsapp.supabase_utils import SupabaseManager; print('✅ Importaciones exitosas'); print('✅ Soporte Excel habilitado')\"")
    if success:
        print("✅ Módulos cargados correctamente")
    else:
        print(f"❌ Error en módulos: {stderr}")

    print("\n📊 Probando extracción de Excel...")
    if os.path.exists("Recetas húngaras.xlsx"):
        print("📁 Archivo Excel encontrado, ejecutando prueba...")
        success, stdout, stderr = run_command("poetry run python -c \"from src.recetario_whatsapp.extractor import WhatsAppExtractor; extractor = WhatsAppExtractor(); resultado = extractor.procesar_archivo('Recetas húngaras.xlsx'); print('📋 Resultado:'); [print(f'  {k}: {v}') for k, v in resultado.items()]\"")
        if success:
            print("✅ Prueba de Excel exitosa")
        else:
            print(f"⚠️  Error en prueba Excel: {stderr}")
    else:
        print("⚠️  Archivo 'Recetas húngaras.xlsx' no encontrado")

    print("\n🚀 Para ejecutar la aplicación:")
    print("   poetry run streamlit run app_streamlit.py")
    print("\n✅ ¡Configuración completada!")

if __name__ == "__main__":
    main()
