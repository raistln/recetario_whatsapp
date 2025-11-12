"""
Utilidades para interactuar con Supabase.
"""

import io
import os
from typing import List, Dict, Any, Optional, Set, Tuple
from supabase import create_client, Client
from datetime import datetime

# Importar cloudinary de manera opcional
try:
    from cloudinary import config as cloudinary_config
    from cloudinary.uploader import upload as cloudinary_upload

    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    print(
        "Warning: Cloudinary not available. Image upload functionality will be disabled."
    )
    # Definir stubs para evitar errores
    cloudinary_config = None
    cloudinary_upload = None


class SupabaseManager:
    """Gestor para operaciones con Supabase."""

    def __init__(self):
        """Inicializa el cliente de Supabase."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas")

        self.client: Client = create_client(url, key)
        self.storage_bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "recetas")
        self.cloudinary_available = CLOUDINARY_AVAILABLE

        # Solo configurar cloudinary si está disponible
        if CLOUDINARY_AVAILABLE:
            cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
            api_key = os.getenv("CLOUDINARY_API_KEY")
            api_secret = os.getenv("CLOUDINARY_API_SECRET")

            if not cloud_name or not api_key or not api_secret:
                print(
                    "Warning: Cloudinary credentials not configured. Image upload will be disabled."
                )
                self.cloudinary_available = False
            else:
                self.cloudinary_folder = os.getenv("CLOUDINARY_FOLDER")
                cloudinary_config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True,
                )

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
            nombre = receta.get("nombre_receta")
            creador = receta.get("creador")
            ingredientes = receta.get("ingredientes")

            if nombre and creador and ingredientes:
                existe = (
                    self.client.table("recetas")
                    .select("id")
                    .eq("creador", creador)
                    .eq("nombre_receta", nombre)
                    .eq("ingredientes", ingredientes)
                    .limit(1)
                    .execute()
                )

                if existe.data:
                    print(
                        f"Receta duplicada detectada: {nombre} de {creador}. Saltando inserción."
                    )
                    return existe.data[0]

            # Preparar los datos para inserción
            imagenes = receta.get("imagenes")
            if imagenes is None:
                imagenes = []

            datos_receta = {
                "creador": receta.get("creador"),
                "nombre_receta": receta.get("nombre_receta"),
                "ingredientes": receta.get("ingredientes"),
                "pasos_preparacion": receta.get("pasos_preparacion"),
                "tiene_foto": receta.get("tiene_foto", False),
                "url_imagen": receta.get("url_imagen"),
                "fecha_mensaje": receta.get("fecha_mensaje"),
                "imagenes": imagenes,
            }

            response = self.client.table("recetas").insert(datos_receta).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            print(f"Error insertando receta: {e}")
            return None

    def obtener_recetas(
        self, filtro_creador: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las recetas, opcionalmente filtradas por creador.

        Args:
            filtro_creador: Nombre del creador para filtrar (opcional)

        Returns:
            Lista de recetas
        """
        try:
            query = self.client.table("recetas").select("*")

            if filtro_creador:
                query = query.eq("creador", filtro_creador)

            response = query.order("fecha_mensaje", desc=True).execute()
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
            response = (
                self.client.table("recetas")
                .select("*")
                .or_(
                    f"nombre_receta.ilike.%{termino_busqueda}%,"
                    f"ingredientes.ilike.%{termino_busqueda}%,"
                    f"creador.ilike.%{termino_busqueda}%"
                )
                .order("fecha_mensaje", desc=True)
                .execute()
            )

            return response.data or []

        except Exception as e:
            print(f"Error buscando recetas: {e}")
            return []

    def actualizar_receta(
        self, receta_id: int, datos_actualizacion: Dict[str, Any]
    ) -> bool:
        """
        Actualiza una receta existente.

        Args:
            receta_id: ID de la receta a actualizar
            datos_actualizacion: Datos a actualizar

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            if (
                "imagenes" in datos_actualizacion
                and datos_actualizacion["imagenes"] is None
            ):
                datos_actualizacion["imagenes"] = []

            response = (
                self.client.table("recetas")
                .update(datos_actualizacion)
                .eq("id", receta_id)
                .execute()
            )
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
            response = (
                self.client.table("recetas").delete().eq("id", receta_id).execute()
            )
            return len(response.data) > 0

        except Exception as e:
            print(f"Error eliminando receta: {e}")
            return False

    def subir_imagen(
        self, archivo_bytes: bytes, nombre_archivo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Sube una imagen a Cloudinary.

        Args:
            archivo_bytes: Bytes del archivo de imagen
            nombre_archivo: Nombre del archivo

        Returns:
            Diccionario con información de la imagen subida o None si hay error
        """
        if not self.cloudinary_available or not CLOUDINARY_AVAILABLE:
            print("Cloudinary not available. Cannot upload image.")
            return None

        try:
            buffer = io.BytesIO(archivo_bytes)
            buffer.seek(0)

            upload_options: Dict[str, Any] = {
                "resource_type": "image",
                "use_filename": True,
                "unique_filename": True,
                "overwrite": False,
            }

            if hasattr(self, "cloudinary_folder") and self.cloudinary_folder:
                upload_options["folder"] = self.cloudinary_folder

            response = cloudinary_upload(buffer, **upload_options)

            if response and response.get("secure_url"):
                return {
                    "url": response.get("secure_url"),
                    "public_id": response.get("public_id"),
                    "version": response.get("version"),
                    "format": response.get("format"),
                    "original_filename": response.get("original_filename")
                    or nombre_archivo,
                }
            return None

        except Exception as e:
            print(f"Error subiendo imagen: {e}")
            return None

    def imagenes_habilitadas(self) -> bool:
        """
        Verifica si las funcionalidades de imagen están habilitadas.

        Returns:
            True si las imágenes están habilitadas, False en caso contrario
        """
        return self.cloudinary_available

    def obtener_creadores_unicos(self) -> List[str]:
        """
        Obtiene la lista de creadores únicos.

        Returns:
            Lista de nombres de creadores
        """
        try:
            response = self.client.table("recetas").select("creador").execute()
            creadores = set()
            for receta in response.data or []:
                creadores.add(receta["creador"])
            return sorted(list(creadores))

        except Exception as e:
            print(f"Error obteniendo creadores: {e}")
            return []

    def obtener_claves_recetas(self) -> Set[Tuple[str, str]]:
        """Devuelve un conjunto con las combinaciones (creador, nombre) ya existentes."""
        claves: Set[Tuple[str, str]] = set()
        try:
            response = (
                self.client.table("recetas").select("creador,nombre_receta").execute()
            )
            for receta in response.data or []:
                creador = (receta.get("creador") or "").strip().lower()
                nombre = (receta.get("nombre_receta") or "").strip().lower()
                if creador and nombre:
                    claves.add((creador, nombre))
        except Exception as e:
            print(f"Error obteniendo claves de recetas: {e}")
        return claves

    def guardar_estado_procesamiento(self, fecha_iso: Optional[str]) -> bool:
        """Guarda la última fecha procesada en Supabase para permitir reanudaciones."""
        try:
            payload = {
                "id": 1,
                "ultima_fecha_iso": fecha_iso,
                "ultima_actualizacion": datetime.utcnow().isoformat(),
            }

            self.client.table("estado_procesamiento").upsert(payload).execute()
            return True
        except Exception as e:
            print(f"Error guardando estado en Supabase: {e}")
            return False

    def obtener_estado_procesamiento(self) -> Optional[str]:
        """Obtiene la última fecha procesada almacenada en Supabase."""
        try:
            response = (
                self.client.table("estado_procesamiento")
                .select("ultima_fecha_iso")
                .eq("id", 1)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0].get("ultima_fecha_iso")
            return None
        except Exception as e:
            print(f"Error obteniendo estado de Supabase: {e}")
            return None
