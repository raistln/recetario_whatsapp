"""
Utilidades para interactuar con Supabase.
"""
import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from datetime import datetime


class SupabaseManager:
    """Gestor para operaciones con Supabase."""
    
    def __init__(self):
        """Inicializa el cliente de Supabase."""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
        
        self.client: Client = create_client(url, key)
        self.storage_bucket = os.getenv('SUPABASE_STORAGE_BUCKET', 'recetas')
    
    def insertar_receta(self, receta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Inserta una nueva receta en la base de datos.
        
        Args:
            receta: Diccionario con los datos de la receta
            
        Returns:
            Diccionario con la receta insertada o None si hay error
        """
        try:
            # Comprobar duplicados por creador + nombre + ingredientes
            nombre = receta.get('nombre_receta')
            creador = receta.get('creador')
            ingredientes = receta.get('ingredientes')

            if nombre and creador and ingredientes:
                existe = self.client.table('recetas').select('id') \
                    .eq('creador', creador) \
                    .eq('nombre_receta', nombre) \
                    .eq('ingredientes', ingredientes) \
                    .limit(1).execute()

                if existe.data:
                    print(f"Receta duplicada detectada: {nombre} de {creador}. Saltando inserción.")
                    return existe.data[0]

            # Preparar los datos para inserción
            datos_receta = {
                'creador': receta.get('creador'),
                'nombre_receta': receta.get('nombre_receta'),
                'ingredientes': receta.get('ingredientes'),
                'pasos_preparacion': receta.get('pasos_preparacion'),
                'tiene_foto': receta.get('tiene_foto', False),
                'url_imagen': receta.get('url_imagen'),
                'fecha_mensaje': receta.get('fecha_mensaje')
            }
            
            response = self.client.table('recetas').insert(datos_receta).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error insertando receta: {e}")
            return None
    
    def obtener_recetas(self, filtro_creador: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las recetas, opcionalmente filtradas por creador.
        
        Args:
            filtro_creador: Nombre del creador para filtrar (opcional)
            
        Returns:
            Lista de recetas
        """
        try:
            query = self.client.table('recetas').select('*')
            
            if filtro_creador:
                query = query.eq('creador', filtro_creador)
            
            response = query.order('fecha_mensaje', desc=True).execute()
            return response.data or []
            
        except Exception as e:
            print(f"Error obteniendo recetas: {e}")
            return []
    
    def buscar_recetas(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """
        Busca recetas por nombre, ingredientes o creador.
        
        Args:
            termino_busqueda: Término a buscar
            
        Returns:
            Lista de recetas que coinciden
        """
        try:
            # Buscar en nombre_receta, ingredientes y creador
            response = self.client.table('recetas').select('*').or_(
                f'nombre_receta.ilike.%{termino_busqueda}%,'
                f'ingredientes.ilike.%{termino_busqueda}%,'
                f'creador.ilike.%{termino_busqueda}%'
            ).order('fecha_mensaje', desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            print(f"Error buscando recetas: {e}")
            return []
    
    def actualizar_receta(self, receta_id: int, datos_actualizacion: Dict[str, Any]) -> bool:
        """
        Actualiza una receta existente.
        
        Args:
            receta_id: ID de la receta a actualizar
            datos_actualizacion: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            response = self.client.table('recetas').update(datos_actualizacion).eq('id', receta_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error actualizando receta: {e}")
            return False
    
    def eliminar_receta(self, receta_id: int) -> bool:
        """
        Elimina una receta.
        
        Args:
            receta_id: ID de la receta a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            response = self.client.table('recetas').delete().eq('id', receta_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error eliminando receta: {e}")
            return False
    
    def subir_imagen(self, archivo_bytes: bytes, nombre_archivo: str) -> Optional[str]:
        """
        Sube una imagen al storage de Supabase.
        
        Args:
            archivo_bytes: Bytes del archivo de imagen
            nombre_archivo: Nombre del archivo
            
        Returns:
            URL de la imagen subida o None si hay error
        """
        try:
            # Generar nombre único para evitar conflictos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_unico = f"{timestamp}_{nombre_archivo}"
            
            response = self.client.storage.from_(self.storage_bucket).upload(
                nombre_unico, 
                archivo_bytes
            )
            
            if response:
                # Obtener URL pública
                url = self.client.storage.from_(self.storage_bucket).get_public_url(nombre_unico)
                return url
            return None
            
        except Exception as e:
            print(f"Error subiendo imagen: {e}")
            return None
    
    def obtener_creadores_unicos(self) -> List[str]:
        """
        Obtiene la lista de creadores únicos.
        
        Returns:
            Lista de nombres de creadores
        """
        try:
            response = self.client.table('recetas').select('creador').execute()
            creadores = set()
            for receta in response.data or []:
                creadores.add(receta['creador'])
            return sorted(list(creadores))
            
        except Exception as e:
            print(f"Error obteniendo creadores: {e}")
            return []
