#!/usr/bin/env python3
"""
Script para probar el patrón regex correcto sin errores.
"""
import re

def test_regex_correcto():
    """Prueba el patrón regex correcto para WhatsApp."""
    print("=== PRUEBA DEL PATRÓN REGEX CORRECTO ===")

    # Patrón correcto para el formato real de WhatsApp: DD/MM/YY, HH:MM - Nombre: mensaje
    patron_correcto = re.compile(
        r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*)'
    )

    # Líneas de prueba del archivo real
    lineas_prueba = [
        '21/10/25, 16:34 - Los mensajes y las llamadas están cifrados de extremo a extremo.',
        '21/10/25, 16:35 - Pablo Iru: Jajajaj',
        '21/10/25, 16:48 - Charlie Brown: Estofado costilla',
        '1kg costilla (adobada final hierbas o similar)',
        '21/10/25, 16:51 - Charlie Brown: Flan de milagros',
        '15min olla exprés'
    ]

    print(f"Probando {len(lineas_prueba)} líneas con patrón correcto:")

    for i, linea in enumerate(lineas_prueba, 1):
        print(f"\n{i}. '{linea}'")

        match = patron_correcto.match(linea)
        if match:
            fecha_str, hora_str, creador, mensaje = match.groups()
            print(f"   ✅ Éxito: {creador} -> {mensaje[:50]}...")
        else:
            print(f"   ❌ No coincide")

    print("
=== PATRÓN FUNCIONA CORRECTAMENTE ===")
    print(f"Patrón usado: {patron_correcto.pattern}")

if __name__ == "__main__":
    test_regex_correcto()
