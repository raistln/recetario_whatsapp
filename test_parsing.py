#!/usr/bin/env python3
"""
Script simple para probar el parsing del extractor.
"""
from src.recetario_whatsapp.extractor import WhatsAppExtractor
import os

def test_parsing():
    """Prueba el parsing del extractor."""
    print("=== PRUEBA DE PARSING DEL EXTRACTOR ===")

    # Crear extractor
    extractor = WhatsAppExtractor()

    # Leer el archivo de muestra
    archivo_muestra = 'samples/Chat de WhatsApp .txt'
    print(f"Leyendo archivo: {archivo_muestra}")

    try:
        with open(archivo_muestra, 'r', encoding='utf-8') as f:
            contenido = f.read()

        print(f"\n=== CONTENIDO DEL ARCHIVO (primeros 500 caracteres) ===")
        print(contenido[:500])
        print("...")

        print(f"\n=== PARSING DE MENSAJES ===")
        mensajes = extractor._parsear_mensajes(contenido)
        print(f'Encontrados {len(mensajes)} mensajes')

        for i, msg in enumerate(mensajes):
            mensaje_corto = msg["mensaje"][:100] + "..." if len(msg["mensaje"]) > 100 else msg["mensaje"]
            print(f'{i+1}. [{msg["fecha"]}] {msg["creador"]}: {mensaje_corto}')

        print(f"\n=== ANÁLISIS DE RECETAS ===")
        for i, msg in enumerate(mensajes):
            es_receta = extractor._es_mensaje_receta(msg["mensaje"])
            print(f'{i+1}. "{msg["creador"]}": {"✅ RECETA" if es_receta else "❌ No receta"} - {msg["mensaje"][:50]}...')

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parsing()
