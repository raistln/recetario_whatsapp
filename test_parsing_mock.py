#!/usr/bin/env python3
"""
Script para probar solo el parsing del extractor sin Mistral.
"""
import re
import os
import sys

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_parsing_sin_mistral():
    """Prueba el parsing sin inicializar Mistral."""
    print("=== PRUEBA DE PARSING SIN MISTRAL ===")

    # Simular la clase WhatsAppExtractor sin inicializar Mistral
    class WhatsAppExtractorMock:
        def __init__(self):
            # No inicializar Mistral ni Supabase
            self.mistral_client = None
            self.supabase_manager = None

            # Solo los patrones regex
            self.patron_mensaje = re.compile(
                r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
            )
            self.patron_mensaje_alternativo = re.compile(
                r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\]\s*-\s*([^:]+):\s*(.*)'
            )

            # Patrón para el formato real del archivo: DD/MM/YY, HH:MM - Nombre: mensaje
            self.patron_mensaje_real = re.compile(
                r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*)'
            )

        def _parsear_mensajes(self, contenido: str):
            """Parsea los mensajes del archivo de WhatsApp."""
            mensajes = []
            lineas = contenido.split('\n')

            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue

                # Intentar patrón principal
                match = self.patron_mensaje.match(linea)
                if match:
                    fecha_str, hora_str, creador, mensaje = match.groups()
                    fecha_completa = f"{fecha_str} {hora_str}"
                    mensajes.append({
                        'fecha': fecha_completa,
                        'creador': creador.strip(),
                        'mensaje': mensaje.strip()
                    })
                    continue

                # Intentar patrón alternativo
                match = self.patron_mensaje_alternativo.match(linea)
                if match:
                    fecha_str, hora_str, creador, mensaje = match.groups()
                    fecha_completa = f"{fecha_str} {hora_str}:00"
                    mensajes.append({
                        'fecha': fecha_completa,
                        'creador': creador.strip(),
                        'mensaje': mensaje.strip()
                    })
                    continue

                # Intentar patrón real del archivo: DD/MM/YY, HH:MM - Nombre: mensaje
                match = self.patron_mensaje_real.match(linea)
                if match:
                    fecha_str, hora_str, creador, mensaje = match.groups()
                    fecha_completa = f"{fecha_str} {hora_str}:00"
                    mensajes.append({
                        'fecha': fecha_completa,
                        'creador': creador.strip(),
                        'mensaje': mensaje.strip()
                    })
                    continue

                # Si no coincide con ningún patrón, podría ser una línea de receta sin formato
                if mensajes and self._es_linea_receta(linea):
                    # Agregar como continuación de la última receta
                    ultimo_mensaje = mensajes[-1]
                    ultimo_mensaje['mensaje'] += f"\n{linea.strip()}"
                    continue

            return mensajes

        def _es_linea_receta(self, texto: str) -> bool:
            """Determina si una línea sin formato de WhatsApp podría ser parte de una receta."""
            texto_lower = texto.lower().strip()

            if not texto_lower:
                return False

            if any(palabra in texto_lower for palabra in ['multimedia omitido', 'cifrado', 'extremo a extremo']):
                return False

            if re.search(r'\d+\s*(g|kg|ml|l|lt|cucharadas?|cuch|cdas?|tazas?|onzas?|piezas?)', texto, re.IGNORECASE):
                return True

            if re.search(r'^\s*[-•*]\s', texto):
                return True

            if re.search(r'^\s*\d+\.?\s*', texto):
                return True

            palabras_receta = [
                'hornear', 'cocinar', 'mezclar', 'batir', 'freír', 'asar', 'hervir',
                'min', 'hora', 'minutos', 'pasos', 'preparación', 'olla', 'sartén',
                'tomates', 'cebolla', 'ajo', 'pimiento', 'patatas', 'carne', 'pollo',
                'pescado', 'arroz', 'pasta', 'salsa', 'estofado', 'guiso', 'sopa'
            ]

            return any(palabra in texto_lower for palabra in palabras_receta)

    # Crear extractor mock
    extractor = WhatsAppExtractorMock()

    # Leer el archivo de muestra
    archivo_muestra = 'samples/Chat de WhatsApp .txt'
    print(f"Leyendo archivo: {archivo_muestra}")

    try:
        with open(archivo_muestra, 'r', encoding='utf-8') as f:
            contenido = f.read()

        print(f"\n=== CONTENIDO DEL ARCHIVO (primeros 300 caracteres) ===")
        print(contenido[:300])
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
    test_parsing_sin_mistral()
