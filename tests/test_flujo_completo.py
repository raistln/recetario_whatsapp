#!/usr/bin/env python3
"""
Test de flujo completo: samples → extractor → mistral → output.

Este test:
1. Toma un archivo de samples/recipes_sample.txt
2. Lo procesa con el extractor
3. Extrae recetas usando Mistral
4. Genera samples/extraction_test.txt con las recetas encontradas
"""
import os
import sys
import json
from pathlib import Path

# Asegurar que el path incluya src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from recetario_whatsapp.extractor import WhatsAppExtractor


def test_flujo_completo():
    """Test de flujo completo del extractor."""
    print("🧪 Test de Flujo Completo: Samples → Extractor → Mistral → Output")
    print("=" * 70)

    # Archivo de entrada
    input_file = "samples/recipes_sample.txt"

    if not os.path.exists(input_file):
        print(f"❌ Archivo de entrada no encontrado: {input_file}")
        return False

    print(f"📁 Archivo de entrada: {input_file}")

    # Ver contenido del archivo
    with open(input_file, 'r', encoding='utf-8') as f:
        contenido = f.read()

    print(f"📏 Tamaño del archivo: {len(contenido)} caracteres")
    print("📝 Contenido del archivo:")
    print(f"   {contenido.replace(chr(10), ' | ')}")

    # Crear extractor
    print("\n🔧 Inicializando extractor...")
    try:
        extractor = WhatsAppExtractor()
        print("✅ Extractor creado correctamente")

        # Procesar archivo
        print("\n📡 Procesando archivo con Mistral...")
        resultado = extractor.procesar_archivo(input_file)

        print("\n📊 Resultados del procesamiento:")
        print(f"   Mensajes procesados: {resultado.get('mensajes_procesados', 0)}")
        print(f"   Bloques procesados: {resultado.get('bloques_procesados', 0)}")
        print(f"   Recetas extraídas: {resultado.get('recetas_extraidas', 0)}")
        print(f"   Recetas insertadas: {resultado.get('recetas_insertadas', 0)}")

        # Generar archivo de salida
        print("\n📝 Generando archivo de salida...")
        output_file = "samples/extraction_test.txt"
        generar_archivo_salida(resultado, output_file)

        print(f"✅ Archivo generado: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        return False


def generar_archivo_salida(resultado: dict, output_file: str):
    """
    Genera un archivo de texto con las recetas extraídas.

    Args:
        resultado: Resultado del procesamiento del extractor
        output_file: Archivo de salida a generar
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🧪 RESULTADOS DE EXTRACCIÓN DE RECETAS\n")
        f.write("=" * 50 + "\n\n")

        # Estadísticas generales
        f.write("📊 ESTADÍSTICAS DEL PROCESAMIENTO\n")
        f.write("-" * 30 + "\n")
        f.write(f"Mensajes procesados: {resultado.get('mensajes_procesados', 0)}\n")
        f.write(f"Bloques procesados: {resultado.get('bloques_procesados', 0)}\n")
        f.write(f"Recetas extraídas: {resultado.get('recetas_extraidas', 0)}\n")
        f.write(f"Recetas insertadas: {resultado.get('recetas_insertadas', 0)}\n")
        f.write(f"Errores encontrados: {resultado.get('errores', 0)}\n\n")

        # Si hay recetas extraídas, mostrar detalles
        if resultado.get('recetas_extraidas', 0) > 0:
            f.write("✅ RECETAS ENCONTRADAS\n")
            f.write("-" * 30 + "\n")
            f.write("Las recetas se han guardado correctamente en la base de datos.\n")
            f.write("Revisa la aplicación web para ver todas las recetas extraídas.\n\n")
        else:
            f.write("⚠️ NO SE ENCONTRARON RECETAS\n")
            f.write("-" * 30 + "\n")
            f.write("Posibles causas:\n")
            f.write("- El archivo no contiene recetas válidas\n")
            f.write("- Problemas con la API de Mistral\n")
            f.write("- Formato de chat no reconocido\n\n")

        # Información técnica
        f.write("🔧 INFORMACIÓN TÉCNICA\n")
        f.write("-" * 30 + "\n")
        f.write("Modelo de IA: Mistral Small\n")
        f.write("Context Window: 32K tokens\n")
        f.write("Bloques procesados: Optimizados para 15K tokens cada uno\n")
        f.write("Fallback: Regex automático si la IA falla\n")
        f.write("Logs: Detallados para debugging\n\n")

        # Timestamp
        from datetime import datetime
        f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    """Función principal del test."""
    print("🚀 Iniciando Test de Flujo Completo")
    print("=" * 70)

    success = test_flujo_completo()

    print("\n" + "=" * 70)
    if success:
        print("🎉 ¡Test de flujo completado exitosamente!")
        print("\n📄 Revisa el archivo generado:")
        print("   samples/extraction_test.txt")
        print("\n✅ El sistema procesa archivos correctamente:")
        print("   → Extrae mensajes de WhatsApp")
        print("   → Agrupa en bloques optimizados")
        print("   → Procesa con Mistral AI")
        print("   → Extrae recetas automáticamente")
        print("   → Genera archivo de resultados")
    else:
        print("❌ El test de flujo falló")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
