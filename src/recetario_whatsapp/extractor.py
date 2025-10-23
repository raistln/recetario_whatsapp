"""
Extractor de recetas desde archivos de chat de WhatsApp.
"""
import re
import json
import os
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .mistral_client import MistralClient
from .supabase_utils import SupabaseManager


class WhatsAppExtractor:
    """Extractor de recetas desde archivos de WhatsApp."""
    
    def __init__(self):
        """Inicializa el extractor con los clientes necesarios."""
        self.mistral_client = MistralClient()
        self.supabase_manager = SupabaseManager()
        
        # Patrones para detectar mensajes de WhatsApp - formato real del archivo
        self.patron_mensaje = re.compile(
            r'\[(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
        )
        self.patron_mensaje_alternativo = re.compile(
            r'\[(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
        )

        # Patrón para el formato real del archivo: DD/MM/YY, HH:MM - Nombre: mensaje
        self.patron_mensaje_real = re.compile(
            r'(\d{2}/\d{2}/\d{2}),\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*)'
        )
    
    def procesar_archivo(self, ruta_archivo: str, fecha_desde: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa un archivo de WhatsApp y extrae recetas.
        
        Args:
            ruta_archivo: Ruta al archivo de WhatsApp
            fecha_desde: Fecha desde la cual procesar (formato YYYY-MM-DD)
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        print(f"Procesando archivo: {ruta_archivo}")
        
        # Leer archivo
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            return {"error": str(e)}
        
        # Parsear mensajes
        mensajes = self._parsear_mensajes(contenido)
        print(f"Encontrados {len(mensajes)} mensajes")
        
        # Determinar fecha mínima a procesar
        fecha_limite = fecha_desde
        if not fecha_limite:
            fecha_limite = self._obtener_fecha_guardada()
            if fecha_limite:
                print(f"Usando fecha guardada: {fecha_limite}")

        # Filtrar por fecha si se especifica
        if fecha_limite:
            mensajes = self._filtrar_por_fecha(mensajes, fecha_limite)
            print(f"Después del filtro desde {fecha_limite}: {len(mensajes)} mensajes")
        
        # Agrupar mensajes consecutivos
        bloques = self._agrupar_mensajes_consecutivos(mensajes)
        print(f"Agrupados en {len(bloques)} bloques")
        
        # Procesar cada bloque
        recetas_extraidas = 0
        recetas_insertadas = 0

        for bloque in bloques:
            print(f"Procesando bloque grande ({len(bloque['texto'])} caracteres)")

            # Mostrar tokens aproximados
            tokens_aprox = len(bloque['texto']) // 4
            print(f"  🔢 Tokens aproximados: {tokens_aprox}")

            # Extraer recetas con Mistral (ahora devuelve múltiples recetas)
            resultado = self.mistral_client.extraer_receta(bloque['texto'])

            if resultado.get('error'):
                print(f"  ❌ Error procesando bloque: {resultado['error']}")
                continue

            # Procesar todas las recetas encontradas en el bloque
            recetas_en_bloque = resultado.get('recetas', [])

            if recetas_en_bloque:
                print(f"  Encontradas {len(recetas_en_bloque)} recetas en el bloque")

                for receta in recetas_en_bloque:
                    # El nuevo formato ya viene con recetas válidas directamente
                    recetas_extraidas += 1
                    print(f"  ✅ Receta: {receta.get('nombre_receta', 'Sin nombre')} de {receta.get('creador')}")

                    # Preparar datos para Supabase
                    datos_receta = {
                        'creador': receta.get('creador'),
                        'nombre_receta': receta.get('nombre_receta'),
                        'ingredientes': receta.get('ingredientes'),
                        'pasos_preparacion': receta.get('pasos_preparacion'),
                        'tiene_foto': receta.get('tiene_foto', False),
                        'url_imagen': None,
                        'fecha_mensaje': receta.get('fecha_mensaje')
                    }

                    # Insertar en Supabase
                    if self.supabase_manager.insertar_receta(datos_receta):
                        recetas_insertadas += 1
                    else:
                        print(f"  ❌ Error insertando receta")
            else:
                print(f"  ℹ️ No se encontraron recetas en el bloque")
        
        # Actualizar estado de procesamiento
        self._actualizar_estado_procesamiento(mensajes[-1]['fecha'] if mensajes else None)
        
        return {
            "mensajes_procesados": len(mensajes),
            "bloques_procesados": len(bloques),
            "recetas_extraidas": recetas_extraidas,
            "recetas_insertadas": recetas_insertadas
        }
    
    def _parsear_mensajes(self, contenido: str) -> List[Dict[str, Any]]:
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
            # Buscar si la línea anterior fue una receta y esta es continuación
            if mensajes and self._es_linea_receta(linea):
                # Agregar como continuación de la última receta
                ultimo_mensaje = mensajes[-1]
                ultimo_mensaje['mensaje'] += f"\n{linea.strip()}"
                continue
        
        return mensajes
    
    def _filtrar_por_fecha(self, mensajes: List[Dict[str, Any]], fecha_desde: str) -> List[Dict[str, Any]]:
        """Filtra mensajes desde una fecha específica."""
        try:
            fecha_limite = datetime.strptime(fecha_desde, '%Y-%m-%d')
            mensajes_filtrados = []
            
            for mensaje in mensajes:
                try:
                    # Convertir fecha del mensaje (formato DD/MM/YY)
                    fecha_mensaje = datetime.strptime(mensaje['fecha'].split()[0], '%d/%m/%y')
                    if fecha_mensaje >= fecha_limite:
                        mensajes_filtrados.append(mensaje)
                except ValueError:
                    # Si no se puede parsear la fecha, incluir el mensaje
                    mensajes_filtrados.append(mensaje)
            
            return mensajes_filtrados
            
        except ValueError:
            print(f"Error en formato de fecha: {fecha_desde}. Usando formato YYYY-MM-DD")
            return mensajes
    
    def _agrupar_mensajes_consecutivos(self, mensajes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Agrupa mensajes en bloques más inteligentes basados en conversación y contenido."""
        if not mensajes:
            return []

        bloques = []

        # Procesar mensajes de manera más granular
        i = 0
        while i < len(mensajes):
            mensaje_actual = mensajes[i]
            texto_actual = mensaje_actual['mensaje'].lower()
            es_receta_actual = self._es_mensaje_receta(texto_actual)

            # Si no es receta, procesar siguiente
            if not es_receta_actual:
                i += 1
                continue

            # Encontramos un mensaje que podría ser receta, buscar mensajes relacionados
            bloque = {
                'creador': mensaje_actual['creador'],
                'fecha': mensaje_actual['fecha'],
                'texto': f"[{mensaje_actual['fecha']}] {mensaje_actual['creador']}: {mensaje_actual['mensaje']}\n"
            }

            # Buscar mensajes consecutivos del mismo autor que puedan ser parte de la misma receta
            j = i + 1
            while j < len(mensajes):
                siguiente_mensaje = mensajes[j]

                # Si cambió de autor o pasaron más de 5 mensajes, parar
                if (siguiente_mensaje['creador'] != mensaje_actual['creador'] or
                    j - i > 5):  # Máximo 5 mensajes consecutivos
                    break

                # Verificar si el siguiente mensaje parece relacionado con receta
                texto_siguiente = siguiente_mensaje['mensaje'].lower()
                if self._es_mensaje_receta_continuacion(texto_siguiente):
                    bloque['texto'] += f"[{siguiente_mensaje['fecha']}] {siguiente_mensaje['creador']}: {siguiente_mensaje['mensaje']}\n"
                    j += 1
                else:
                    break

            # Agregar bloque si tiene contenido
            if bloque['texto'].strip():
                bloques.append(bloque)

            i = j  # Saltar los mensajes que ya procesamos

        return bloques

    def _es_mensaje_receta(self, texto: str) -> bool:
        """Determina si un mensaje individual parece contener una receta."""
        texto_lower = texto.lower()

        # Palabras clave que indican inicio de receta
        indicadores_receta = [
            'receta:', 'receta de', 'ingredientes:',
            'receta'  # Permitir "receta" suelto ahora
        ]

        # Palabras que sugieren nombres de recetas
        palabras_receta = [
            'estofado', 'flan', 'torta', 'salsa', 'guiso', 'sopa', 'ensalada',
            'pasta', 'arroz', 'pescado', 'carne', 'pollo', 'verduras',
            'costilla', 'milagros', 'teriyaki', 'césar', 'patatas'
        ]

        # Patrones de cantidades (números seguidos de unidades de medida)
        patrones_cantidad = [
            r'\d+\s*(g|kg|ml|l|lt|onzas?|onz|tazas?|taza|cucharadas?|cucharada|cuch|cdas?|cdita)',
            r'\d+\s*(piezas?|unidades?|uds?\.?|pz|pz\.?)',
            r'\d+\s*(kg|gr|mg|cl|dl)'  # Más unidades
        ]
        tiene_cantidades = any(re.search(patron, texto, re.IGNORECASE) for patron in patrones_cantidad)

        # Verificar si parece nombre de receta
        tiene_palabras_receta = any(palabra in texto_lower for palabra in palabras_receta)

        # Verificar indicadores específicos
        tiene_indicador_especifico = any(indicador in texto_lower for indicador in indicadores_receta)

        # Considerar receta si:
        # 1. Tiene indicador específico
        # 2. Tiene palabras de receta + cantidades
        # 3. Tiene palabras de receta + parece nombre corto
        if tiene_indicador_especifico:
            return True

        if tiene_palabras_receta and (tiene_cantidades or len(texto.split()) <= 3):
            return True

        # Para casos sin indicador específico, ser más permisivo
        palabras_cocina = ['hornear', 'cocinar', 'mezclar', 'batir', 'freír', 'asar', 'hervir', '15min', 'olla']
        tiene_palabras_cocina = any(palabra in texto_lower for palabra in palabras_cocina)

        return tiene_cantidades and tiene_palabras_cocina

    def _es_mensaje_receta_continuacion(self, texto: str) -> bool:
        """Determina si un mensaje parece ser continuación de una receta."""
        texto_lower = texto.lower()

        # Palabras clave de continuación
        continuacion = [
            'ingredientes', 'pasos', 'preparación', 'receta',
            '-', '•', '*',  # Marcadores de lista
            'mezclar', 'hornear', 'cocinar', 'batir', 'revolver',  # Acciones de cocina
        ]

        # Si tiene guiones al inicio (listas)
        tiene_guiones = bool(re.search(r'^\s*[-•*]\s', texto))

        # Si tiene números al inicio (pasos numerados)
        tiene_numeros = bool(re.search(r'^\s*\d+\.?\s*', texto))

        # Si tiene palabras de continuación
        tiene_palabras = any(palabra in texto_lower for palabra in continuacion)

        # Si tiene cantidades
        tiene_cantidades = bool(re.search(r'\d+\s*(g|kg|ml|l|lt|cucharadas?|cuch|cdas?|tazas?|onzas?|piezas?)', texto, re.IGNORECASE))

        return tiene_guiones or tiene_numeros or tiene_palabras or tiene_cantidades
    
    def _es_linea_receta(self, texto: str) -> bool:
        """Determina si una línea sin formato de WhatsApp podría ser parte de una receta."""
        texto_lower = texto.lower().strip()
        
        # Si está vacía, no es receta
        if not texto_lower:
            return False
        
        # Si parece un mensaje del sistema de WhatsApp, no es receta
        if any(palabra in texto_lower for palabra in ['multimedia omitido', 'cifrado', 'extremo a extremo']):
            return False
        
        # Si tiene cantidades, probablemente es receta
        if re.search(r'\d+\s*(g|kg|ml|l|lt|cucharadas?|cuch|cdas?|tazas?|onzas?|piezas?)', texto, re.IGNORECASE):
            return True
        
        # Si tiene guiones al inicio (listas)
        if re.search(r'^\s*[-•*]\s', texto):
            return True
        
        # Si tiene números al inicio (pasos numerados)
        if re.search(r'^\s*\d+\.?\s*', texto):
            return True
        
        # Palabras que sugieren ingredientes o pasos
        palabras_receta = [
            'hornear', 'cocinar', 'mezclar', 'batir', 'freír', 'asar', 'hervir', 
            'min', 'hora', 'minutos', 'pasos', 'preparación', 'olla', 'sartén',
            'tomates', 'cebolla', 'ajo', 'pimiento', 'patatas', 'carne', 'pollo',
            'pescado', 'arroz', 'pasta', 'salsa', 'estofado', 'guiso', 'sopa'
        ]
        
        return any(palabra in texto_lower for palabra in palabras_receta)
    
    def _es_candidato_receta(self, texto: str) -> bool:
        """Determina si un bloque de texto puede contener recetas."""
        # Para bloques grandes, siempre procesamos (más eficiente que filtrar)
        # ya que Mistral puede identificar mejor qué es receta y qué no
        return True

        # Comentado el código anterior para simplificar
        """
        texto_lower = texto.lower()

        # Palabras clave que indican receta
        palabras_clave = ['ingredientes', 'receta', 'pasos', 'preparación']
        tiene_palabras_clave = any(palabra in texto_lower for palabra in palabras_clave)

        # Patrones de lista (guiones, bullets, cantidades)
        patrones_lista = [
            r'^\s*[-•]\s+',  # Guiones o bullets
            r'\d+\s*[gkgmltazas]',  # Cantidades con unidades
            r'\d+\s+[a-zA-Z]',  # Número seguido de palabra
        ]
        tiene_patrones_lista = any(re.search(patron, texto, re.MULTILINE) for patron in patrones_lista)

        return tiene_palabras_clave or tiene_patrones_lista
        """
    
    def _actualizar_estado_procesamiento(self, ultima_fecha: Optional[str]):
        """Actualiza el archivo de estado con la última fecha procesada."""
        estado = {
            "ultima_fecha_procesada": ultima_fecha,
            "ultima_fecha_iso": None,
            "ultima_actualizacion": datetime.now().isoformat()
        }

        if ultima_fecha:
            try:
                fecha_dt = datetime.strptime(ultima_fecha, '%d/%m/%y %H:%M:%S')
                estado["ultima_fecha_iso"] = fecha_dt.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    fecha_dt = datetime.strptime(ultima_fecha.split()[0], '%d/%m/%y')
                    estado["ultima_fecha_iso"] = fecha_dt.strftime('%Y-%m-%d')
                except ValueError:
                    pass

        # Guardar estado en Supabase si es posible
        try:
            if self.supabase_manager:
                self.supabase_manager.guardar_estado_procesamiento(estado["ultima_fecha_iso"])
        except Exception as e:
            print(f"Error guardando estado en Supabase: {e}")

        try:
            os.makedirs('state', exist_ok=True)
            with open('state/last_processed.json', 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando estado: {e}")

    def _obtener_fecha_guardada(self) -> Optional[str]:
        """Obtiene la fecha guardada del último procesamiento en formato YYYY-MM-DD."""
        # Priorizar estado persistido en Supabase
        try:
            if self.supabase_manager:
                fecha_supabase = self.supabase_manager.obtener_estado_procesamiento()
                if fecha_supabase:
                    return fecha_supabase
        except Exception as e:
            print(f"Error leyendo estado de Supabase: {e}")

        ruta_estado = os.path.join('state', 'last_processed.json')

        if not os.path.exists(ruta_estado):
            return None

        try:
            with open(ruta_estado, 'r', encoding='utf-8') as f:
                estado = json.load(f)

            fecha_iso = estado.get('ultima_fecha_iso')
            if fecha_iso:
                return fecha_iso

            # Intentar convertir el formato antiguo si existe
            fecha_original = estado.get('ultima_fecha_procesada')
            if not fecha_original:
                return None

            try:
                fecha_dt = datetime.strptime(fecha_original, '%d/%m/%y %H:%M:%S')
                return fecha_dt.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    fecha_dt = datetime.strptime(fecha_original.split()[0], '%d/%m/%y')
                    return fecha_dt.strftime('%Y-%m-%d')
                except ValueError:
                    return None

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error leyendo estado previo: {e}")
            return None


def main():
    """Función principal para ejecutar el extractor desde línea de comandos."""
    parser = argparse.ArgumentParser(description='Extraer recetas de archivos de WhatsApp')
    parser.add_argument('--file', required=True, help='Ruta al archivo de WhatsApp')
    parser.add_argument('--fecha-desde', help='Fecha desde la cual procesar (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Crear extractor y procesar
    extractor = WhatsAppExtractor()

    fecha_desde = args.fecha_desde
    if not fecha_desde:
        fecha_desde = extractor._obtener_fecha_guardada()
        if fecha_desde:
            print(f"Usando fecha guardada por defecto: {fecha_desde}")

    resultado = extractor.procesar_archivo(args.file, fecha_desde)
    
    print("\n=== RESUMEN ===")
    print(f"Mensajes procesados: {resultado.get('mensajes_procesados', 0)}")
    print(f"Bloques procesados: {resultado.get('bloques_procesados', 0)}")
    print(f"Recetas extraídas: {resultado.get('recetas_extraidas', 0)}")
    print(f"Recetas insertadas: {resultado.get('recetas_insertadas', 0)}")


if __name__ == "__main__":
    main()

