#!/usr/bin/env python3
"""
Script simple para probar el parsing básico sin dependencias externas.
"""
import re

def test_regex_patterns():
    """Prueba los patrones regex para el formato de WhatsApp."""
    print("=== PRUEBA DE PATRONES REGEX ===")

    # Patrones para detectar mensajes de WhatsApp
    patron_mensaje = re.compile(
        r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
    )
    patron_mensaje_alternativo = re.compile(
        r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\]\s*-\s*([^:]+):\s*(.*)'
    )

    # Patrón para el formato real del archivo: DD/MM/YY, HH:MM - Nombre: mensaje
    patron_mensaje_real = re.compile(
        r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*)'
    )

    # Líneas de prueba del archivo de WhatsApp
    lineas_prueba = [
        '21/10/25, 16:34 - Los mensajes y las llamadas están cifrados de extremo a extremo.',
        '21/10/25, 16:35 - Pablo Iru: Jajajaj',
        '21/10/25, 16:48 - Charlie Brown: Estofado costilla',
        '1kg costilla (adobada final hierbas o similar)',
        '1kg patatas',
        '15min olla exprés'
    ]

    print(f"Probando {len(lineas_prueba)} líneas:")

    for i, linea in enumerate(lineas_prueba, 1):
        print(f"\n{i}. '{linea}'")

        # Probar patrón principal
        match = patron_mensaje.match(linea)
        if match:
            fecha_str, hora_str, creador, mensaje = match.groups()
            print(f"   ✅ Patrón principal: {creador} -> {mensaje[:50]}...")
            continue

        # Probar patrón alternativo
        match = patron_mensaje_alternativo.match(linea)
        if match:
            fecha_str, hora_str, creador, mensaje = match.groups()
            print(f"   ✅ Patrón alternativo: {creador} -> {mensaje[:50]}...")
            continue

        # Probar patrón real
        match = patron_mensaje_real.match(linea)
        if match:
            fecha_str, hora_str, creador, mensaje = match.groups()
            print(f"   ✅ Patrón real: {creador} -> {mensaje[:50]}...")
            continue

        # Si no coincide con ningún patrón, podría ser línea de receta
        if re.search(r'\d+\s*(g|kg|ml|l|lt|cucharadas?|cuch|cdas?|tazas?|onzas?|piezas?)', linea, re.IGNORECASE):
            print(f"   🔍 Posible línea de receta: {linea}")
        else:
            print(f"   ❌ No coincide con ningún patrón")

if __name__ == "__main__":
    test_regex_patterns()
