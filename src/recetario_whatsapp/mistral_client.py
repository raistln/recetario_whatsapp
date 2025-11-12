"""
Cliente para la API de Mistral para extraer recetas de texto de WhatsApp.
"""

import json
import os
import re
import time
from typing import Dict, Any, Optional, List
from mistralai import Mistral


class MistralClient:
    """Cliente para interactuar con la API de Mistral."""

    def __init__(self):
        """Inicializa el cliente con la API key desde variables de entorno."""
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY no encontrada en las variables de entorno"
            )

        # Usar Mistral Small para eficiencia y menor costo
        self.model = "mistral-small-latest"

        # Configuración optimizada para tokens (Mistral Small tiene menos context)
        self.max_tokens_output = 2000  # Límite para la respuesta
        self.context_window = 32000  # Context window de Mistral Small (suficiente)
        self.max_reintentos = int(os.getenv("MISTRAL_MAX_REINTENTOS", "3"))
        self.reintento_delay = float(os.getenv("MISTRAL_REINTENTO_DELAY", "2"))
        self.delay_entre_llamadas = float(os.getenv("MISTRAL_DELAY_SEG", "1.5"))
        self._ultimo_llamado = 0.0

    def calcular_tokens_aproximado(self, texto: str) -> int:
        """
        Calcula una aproximación de tokens en un texto.
        Regla general: ~4 caracteres por token en inglés/español.

        Args:
            texto: Texto a calcular

        Returns:
            Número aproximado de tokens
        """
        # Aproximación: 1 token ≈ 4 caracteres (incluyendo espacios y puntuación)
        tokens = len(texto) // 4

        # Agregar tokens para el prompt del sistema
        prompt_tokens = len(self._crear_prompt_extraccion()) // 4

        return tokens + prompt_tokens

    def verificar_limite_tokens(self, texto_bloque: str) -> bool:
        """
        Verifica si el texto cabe en el context window.

        Args:
            texto_bloque: Texto a verificar

        Returns:
            True si cabe, False si excede el límite
        """
        total_tokens = self.calcular_tokens_aproximado(texto_bloque)

        # Dejar espacio para la respuesta (max_tokens_output)
        disponible = self.context_window - self.max_tokens_output

        return total_tokens <= disponible

    def extraer_receta(self, texto_bloque: str) -> Dict[str, Any]:
        """
        Extrae recetas de un bloque de texto usando Mistral.

        Args:
            texto_bloque: Bloque de texto de WhatsApp a procesar

        Returns:
            Diccionario con las recetas extraídas o error
        """
        # Verificar límite de tokens
        if not self.verificar_limite_tokens(texto_bloque):
            return {
                "recetas": [],
                "error": f"Texto demasiado largo ({self.calcular_tokens_aproximado(texto_bloque)} tokens). Límite: {self.context_window - self.max_tokens_output} tokens",
            }

        prompt = self._crear_prompt_extraccion()

        for intento in range(self.max_reintentos):
            try:
                self._respetar_intervalo_minimo()
                # Usar la API con context manager (sintaxis correcta)
                with Mistral(api_key=self.api_key) as client:
                    response = client.chat.complete(
                        model=self.model,
                        messages=[
                            {
                                "role": "user",
                                "content": f"{prompt}\n\nTexto del chat de WhatsApp:\n{texto_bloque}",
                            }
                        ],
                        temperature=0.1,
                        max_tokens=self.max_tokens_output,
                    )

                respuesta = response.choices[0].message.content.strip()
                self._ultimo_llamado = time.time()
                print(f"  🤖 Respuesta de Mistral ({len(respuesta)} caracteres):")
                print(f"  📝 {respuesta[:200]}{'...' if len(respuesta) > 200 else ''}")

                # Intentar parsear la respuesta como JSON
                try:
                    resultado = json.loads(respuesta)

                    # Si la respuesta tiene el formato nuevo con array de recetas
                    if isinstance(resultado, dict) and "recetas" in resultado:
                        return resultado
                    else:
                        # Si es el formato antiguo con una sola receta
                        return {
                            "recetas": [resultado] if resultado.get("es_receta") else []
                        }

                except json.JSONDecodeError as e:
                    print(f"  ❌ Error JSON: {e}")
                    print(f"  📄 Respuesta completa: {respuesta}")

                    # Intentar extraer JSON de la respuesta si está embebido en texto
                    json_match = re.search(r"\{.*\}", respuesta, re.DOTALL)
                    if json_match:
                        try:
                            resultado = json.loads(json_match.group())
                            print(f"  ✅ JSON extraído del texto")
                            return resultado
                        except json.JSONDecodeError:
                            pass

                    # Intentar encontrar recetas en el texto usando regex más simple
                    print(f"  🔍 Intentando extraer recetas del texto...")
                    recetas_encontradas = self._extraer_recetas_simple(
                        texto_bloque, respuesta
                    )

                    if recetas_encontradas:
                        print(f"  ✅ Recetas extraídas con método simple")
                        return {"recetas": recetas_encontradas}

                    # Si no es JSON válido, devolver array vacío
                    return {"recetas": [], "error": "Respuesta no válida de Mistral"}

            except Exception as e:
                error_str = str(e)
                es_capacidad = any(
                    term in error_str.lower()
                    for term in ["429", "capacity", "service tier"]
                )
                if es_capacidad and intento < self.max_reintentos - 1:
                    espera = self.reintento_delay * (intento + 1)
                    print(
                        f"  ⏳ Error de capacidad, reintento {intento + 1}/{self.max_reintentos - 1} en {espera:.1f}s"
                    )
                    time.sleep(espera)
                    continue

                if es_capacidad:
                    print("  ⚠️ Aplicando fallback regex por capacidad llena")
                    recetas_fallback = self._extraer_recetas_simple(texto_bloque, "")
                    if recetas_fallback:
                        return {
                            "recetas": recetas_fallback,
                            "warning": "fallback_regex",
                        }

                return {
                    "recetas": [],
                    "error": f"Error en la API de Mistral: {error_str}",
                }

        return {
            "recetas": [],
            "error": "Error en la API de Mistral tras múltiples reintentos",
        }

    def _respetar_intervalo_minimo(self) -> None:
        """Espera el tiempo necesario entre llamadas consecutivas a la API."""
        if self.delay_entre_llamadas <= 0:
            return

        transcurrido = time.time() - self._ultimo_llamado
        restante = self.delay_entre_llamadas - transcurrido

        if restante > 0:
            print(f"  ⏳ Esperando {restante:.1f}s antes de llamar a Mistral")
            time.sleep(restante)

    def _extraer_recetas_simple(
        self, texto_original: str, respuesta_mistral: str
    ) -> List[Dict[str, Any]]:
        """
        Método de fallback: extrae recetas directamente del texto usando regex.

        Args:
            texto_original: Texto del chat original
            respuesta_mistral: Respuesta de Mistral (para logging)

        Returns:
            Lista de recetas encontradas
        """
        recetas = []

        # Buscar patrones de recetas en el texto original
        # Patrón: [fecha] Nombre: receta con ingredientes y pasos
        patron_receta = r"\[(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+?)(?=\n\[|\n$|$)"

        matches = re.findall(patron_receta, texto_original, re.DOTALL | re.MULTILINE)

        for match in matches:
            fecha, hora, creador, contenido = match

            # Verificar si el contenido parece una receta (ingredientes o pasos)
            contenido_lower = contenido.lower()

            # Buscar ingredientes (cantidades + palabras de comida)
            tiene_ingredientes = bool(
                re.search(r"\d+\s*[gkgmltazas]?\s+[a-zA-Z]", contenido)
            ) or bool(re.search(r"\d+\s+[a-zA-Z]", contenido))

            # Buscar pasos de preparación
            tiene_pasos = bool(
                re.search(r"\d+\.|\-|\•|hornear|cocinar|freír|mezclar", contenido_lower)
            )

            if tiene_ingredientes or tiene_pasos:
                # Extraer nombre de receta (primera línea o título)
                lineas = contenido.strip().split("\n")
                nombre_receta = lineas[0].strip() if lineas else None

                # Separar ingredientes y pasos
                ingredientes = ""
                pasos = ""

                # Buscar donde terminan los ingredientes y empiezan los pasos
                ingredientes_end = -1

                for i, linea in enumerate(lineas):
                    if re.search(
                        r"pasos?|preparación|instrucciones|modo de hacer", linea.lower()
                    ):
                        ingredientes_end = i
                        break

                if ingredientes_end > 0:
                    ingredientes = "\n".join(lineas[:ingredientes_end])
                    pasos = "\n".join(lineas[ingredientes_end:])
                else:
                    # Si no hay separación clara, todo son ingredientes
                    ingredientes = "\n".join(lineas)

                # Crear fecha ISO
                try:
                    from datetime import datetime

                    fecha_obj = datetime.strptime(
                        f"20{fecha.replace('/', '-')}", "%Y-%d-%m"
                    )
                    fecha_iso = fecha_obj.strftime("%Y-%m-%d") + f"T{hora}:00+00:00"
                except:
                    fecha_iso = "2025-01-01T00:00:00+00:00"

                receta = {
                    "creador": creador.strip(),
                    "nombre_receta": nombre_receta if nombre_receta else None,
                    "ingredientes": ingredientes.strip(),
                    "pasos_preparacion": pasos.strip() if pasos.strip() else None,
                    "tiene_foto": "imagen" in contenido_lower
                    or "foto" in contenido_lower,
                    "fecha_mensaje": fecha_iso,
                }

                recetas.append(receta)

        print(f"  🔄 Fallback encontró {len(recetas)} recetas con regex")
        return recetas

    def _crear_prompt_extraccion(self) -> str:
        """Crea el prompt para la extracción de recetas."""
        return """Extrae recetas de este chat. Responde SOLO con JSON válido.

IMPORTANTE:
- Los INGREDIENTES son OBLIGATORIOS - sin ellos NO es una receta válida
- Los ingredientes pueden estar marcados con "-", "*", números, o separados por comas
- Los pasos pueden empezar con números, guiones, o palabras como "mezclar", "hornear", "cocinar"
- Si encuentras "Ingredientes:" o "Pasos:" úsalos como separadores
- Combina mensajes del mismo autor si forman parte de la misma receta

Ejemplo 1 (ingredientes en una línea):
Input: "Charlie Brown: Estofado costilla 1kg costilla, 1kg patatas, 15min olla exprés"
Output: {"recetas": [{"creador": "Charlie Brown", "nombre_receta": "Estofado costilla", "ingredientes": "1kg costilla, 1kg patatas", "pasos_preparacion": "15min olla exprés", "tiene_foto": false, "fecha_mensaje": "2025-01-01T00:00:00+00:00"}]}

Ejemplo 2 (ingredientes en lista):
Input: "[01/10/25, 18:02:13] Ana: Ingredientes:\n- 200 g harina\n- 100 g azúcar\n- 2 huevos\nPasos:\n1. Mezclar todo.\n2. Hornear 30 minutos."
Output: {"recetas": [{"creador": "Ana", "nombre_receta": "Receta de Ana", "ingredientes": "200 g harina, 100 g azúcar, 2 huevos", "pasos_preparacion": "Mezclar todo. Hornear 30 minutos.", "tiene_foto": false, "fecha_mensaje": "2025-10-01T18:02:13+00:00"}]}

Ejemplo 3 (receta con imagen):
Input: "[02/10/25, 12:10:01] Marta: Receta: Gazpacho\nIngredientes:\n- 1 kg tomates\n- 1 pepino\n- 1 pimiento\nPasos:\nTriturar y refrigerar.\n<adjunto: imagen incluida>"
Output: {"recetas": [{"creador": "Marta", "nombre_receta": "Gazpacho", "ingredientes": "1 kg tomates, 1 pepino, 1 pimiento", "pasos_preparacion": "Triturar y refrigerar.", "tiene_foto": true, "fecha_mensaje": "2025-10-02T12:10:01+00:00"}]}

REGLAS CRÍTICAS:
- INGREDIENTES son OBLIGATORIOS - si no hay ingredientes, no es una receta válida
- Combina todos los ingredientes en un solo campo de texto separado por comas
- Combina todos los pasos en un solo campo de texto
- Usa el nombre EXACTO de la persona del mensaje
- Si hay "<adjunto:" o "imagen" marca "tiene_foto": true
- Si no hay recetas válidas (sin ingredientes): {"recetas": []}
- NO agregues texto fuera del JSON"""
