"""
Aplicación Streamlit para el recetario de WhatsApp.
Versión corregida para ejecutar directamente.
"""
import streamlit as st
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import io

# Agregar el directorio src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar módulos del proyecto
from recetario_whatsapp.supabase_utils import SupabaseManager
from recetario_whatsapp.extractor import WhatsAppExtractor

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="🍳 Recetario WhatsApp",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar clientes
@st.cache_resource
def get_supabase_manager():
    """Obtiene el gestor de Supabase (con caché)."""
    try:
        return SupabaseManager()
    except Exception as e:
        st.error(f"Error conectando con Supabase: {e}")
        return None

@st.cache_resource
def get_extractor():
    """Obtiene el extractor de WhatsApp (con caché)."""
    try:
        return WhatsAppExtractor()
    except Exception as e:
        st.error(f"Error inicializando extractor: {e}")
        return None


def main():
    """Función principal de la aplicación."""
    st.title("🍳 Recetario WhatsApp")
    st.markdown("---")
    
    # Inicializar clientes
    supabase_manager = get_supabase_manager()
    extractor = get_extractor()
    
    if not supabase_manager or not extractor:
        st.error("No se pudieron inicializar los servicios necesarios. Verifica la configuración.")
        return
    
    def mantener_expander_abierto(clave_estado: str) -> None:
        """Marca un expander como abierto en session_state."""
        st.session_state[clave_estado] = True

    # Sidebar para filtros y búsqueda
    with st.sidebar:
        st.header("🔍 Filtros y Búsqueda")
        
        # Búsqueda por texto
        termino_busqueda = st.text_input("Buscar recetas", placeholder="Ingrediente, nombre, creador...")
        
        # Filtro por creador
        creadores = supabase_manager.obtener_creadores_unicos()
        creador_filtro = st.selectbox("Filtrar por creador", ["Todos"] + creadores)
        
        # Configuración de módulos
        st.markdown("---")
        st.header("⚙️ Configuración")

        # Opción para desactivar imágenes - solo si están disponibles
        if supabase_manager.imagenes_habilitadas():
            imagenes_habilitadas = st.checkbox(
                "📷 Habilitar módulo de imágenes",
                value=True,
                help="Activa solo si quieres gestionar fotos de recetas"
            )
        else:
            imagenes_habilitadas = False
            st.info("📷 Módulo de imágenes no disponible (falta configuración de Cloudinary)")
        
        # Botón para agregar receta manualmente
        st.markdown("---")
        st.header("➕ Agregar Receta")
        
        if st.button("📝 Crear Nueva Receta", type="primary"):
            st.session_state['mostrar_formulario_nueva'] = True
        
        # Botón para procesar nuevo archivo
        st.markdown("---")
        st.header("📁 Procesar Archivo")
        archivo_subido = st.file_uploader(
            "Subir archivo de WhatsApp o Excel",
            type=['txt', 'xlsx', 'xls'],
            help="Sube un archivo .txt exportado de WhatsApp o un archivo Excel (.xlsx, .xls) con recetas"
        )
        
        if archivo_subido:
            if st.button("Procesar Archivo"):
                with st.spinner("Procesando archivo..."):
                    # Detectar tipo de archivo por extensión
                    nombre_archivo = archivo_subido.name.lower()

                    if nombre_archivo.endswith(('.xlsx', '.xls')):
                        # Procesar como Excel
                        with open('temp_excel.xlsx', 'wb') as f:
                            f.write(archivo_subido.read())

                        # Procesar archivo Excel
                        resultado = extractor.procesar_archivo('temp_excel.xlsx')

                        # Limpiar archivo temporal
                        import os
                        if os.path.exists('temp_excel.xlsx'):
                            os.remove('temp_excel.xlsx')

                    else:
                        # Procesar como WhatsApp (txt)
                        contenido = archivo_subido.read().decode('utf-8')
                        with open('temp_whatsapp.txt', 'w', encoding='utf-8') as f:
                            f.write(contenido)

                        # Procesar archivo WhatsApp
                        resultado = extractor.procesar_archivo('temp_whatsapp.txt')

                        # Limpiar archivo temporal
                        if os.path.exists('temp_whatsapp.txt'):
                            os.remove('temp_whatsapp.txt')

                    # Mostrar resultados
                    if resultado.get('error'):
                        st.error(f"❌ Error procesando archivo: {resultado['error']}")
                    else:
                        st.success(f"✅ Archivo procesado exitosamente!")

                        # Mostrar estadísticas según el tipo de archivo
                        if resultado.get('archivo_tipo') == 'excel':
                            st.info(f"""
                            **Resumen del procesamiento:**
                            - Hojas procesadas: {resultado.get('hojas_procesadas', 0)}
                            - Recetas extraídas: {resultado.get('recetas_extraidas', 0)}
                            - Recetas insertadas: {resultado.get('recetas_insertadas', 0)}
                            """)
                        else:
                            st.info(f"""
                            **Resumen del procesamiento:**
                            - Mensajes procesados: {resultado.get('mensajes_procesados', 0)}
                            - Bloques procesados: {resultado.get('bloques_procesados', 0)}
                            - Recetas extraídas: {resultado.get('recetas_extraidas', 0)}
                            - Recetas insertadas: {resultado.get('recetas_insertadas', 0)}
                            """)

                        # Recargar recetas
                        st.rerun()
    
    # Formulario para crear nueva receta
    if st.session_state.get('mostrar_formulario_nueva', False):
        st.header("📝 Crear Nueva Receta")
        
        with st.form("form_nueva_receta"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_creador = st.text_input(
                    "👤 Nombre del creador",
                    placeholder="Ej: Ana García, Charlie Brown..."
                )
                nuevo_nombre = st.text_input(
                    "🍽️ Nombre de la receta",
                    placeholder="Ej: Estofado costilla, Torta de chocolate..."
                )
            
            with col2:
                nuevos_ingredientes = st.text_area(
                    "🥘 Ingredientes",
                    placeholder="Ej:\n- 200g harina\n- 100g azúcar\n- 2 huevos",
                    height=100
                )
                nuevos_pasos = st.text_area(
                    "👨‍🍳 Pasos de preparación",
                    placeholder="Ej:\n1. Mezclar todo\n2. Hornear 30 minutos",
                    height=100
                )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.form_submit_button("💾 Crear Receta", type="primary"):
                    if not nuevo_creador or not nuevo_nombre or not nuevos_ingredientes:
                        st.error("Los campos de creador, nombre y ingredientes son obligatorios")
                    else:
                        nueva_receta = {
                            'creador': nuevo_creador,
                            'nombre_receta': nuevo_nombre,
                            'ingredientes': nuevos_ingredientes,
                            'pasos_preparacion': nuevos_pasos if nuevos_pasos else None,
                            'tiene_foto': False,
                            'fecha_mensaje': datetime.now().isoformat()
                        }
                        
                        resultado = supabase_manager.insertar_receta(nueva_receta)
                        if resultado:
                            st.success(f"✅ Receta '{nuevo_nombre}' creada correctamente")
                            st.session_state['mostrar_formulario_nueva'] = False
                            st.rerun()
                        else:
                            st.error("❌ Error creando la receta")
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state['mostrar_formulario_nueva'] = False
                    st.rerun()
        
        st.markdown("---")
    
    # Obtener recetas según filtros
    if termino_busqueda:
        recetas = supabase_manager.buscar_recetas(termino_busqueda)
    elif creador_filtro != "Todos":
        recetas = supabase_manager.obtener_recetas(creador_filtro)
    else:
        recetas = supabase_manager.obtener_recetas()
    
    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Recetas", len(recetas))
    with col2:
        st.metric("Creadores", len(set(r['creador'] for r in recetas)))
    with col3:
        if supabase_manager.imagenes_habilitadas() and imagenes_habilitadas:
            st.metric("Con Fotos", len([r for r in recetas if r.get('tiene_foto')]))
        elif supabase_manager.imagenes_habilitadas():
            st.metric("Módulo Imágenes", "Desactivado")
        else:
            st.metric("Módulo Imágenes", "No disponible")
    
    st.markdown("---")
    
    # Mostrar recetas
    if not recetas:
        st.info("No se encontraron recetas. ¡Sube un archivo de WhatsApp para empezar!")
        return
    
    for i, receta in enumerate(recetas):
        # Inicializar key para resetear uploader
        if f'upload_key_{i}' not in st.session_state:
            st.session_state[f'upload_key_{i}'] = 0

        expander_state_key = f'expander_abierto_{receta["id"]}'
        if expander_state_key not in st.session_state:
            st.session_state[expander_state_key] = False

        with st.expander(
            f"🍽️ {receta.get('nombre_receta', 'Receta sin nombre')} - {receta['creador']}",
            expanded=st.session_state[expander_state_key]
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Mostrar ingredientes
                st.subheader("🥘 Ingredientes")
                st.text(receta.get('ingredientes', 'No especificados'))
                
                # Mostrar pasos
                if receta.get('pasos_preparacion'):
                    st.subheader("👨‍🍳 Preparación")
                    st.text(receta.get('pasos_preparacion'))
                
                # Mostrar información adicional
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.caption(f"👤 Creador: {receta['creador']}")
                with col_info2:
                    if receta.get('fecha_mensaje'):
                        st.caption(f"📅 Fecha: {receta['fecha_mensaje'][:10]}")
            
            with col2:
                # Mostrar imágenes solo si está habilitado
                if supabase_manager.imagenes_habilitadas() and imagenes_habilitadas:
                    imagenes_receta = receta.get('imagenes') or []

                    # Compatibilidad con recetas antiguas que solo tienen url_imagen
                    if not imagenes_receta and receta.get('url_imagen'):
                        imagenes_receta = [{'url': receta['url_imagen'], 'autor': receta.get('creador')}]

                    if imagenes_receta:
                        total_imagenes = len(imagenes_receta)
                        
                        # Usar session_state para el índice del carrusel
                        carousel_key = f"carousel_{receta['id']}"
                        if carousel_key not in st.session_state:
                            st.session_state[carousel_key] = 0
                        
                        indice = st.session_state[carousel_key]
                        
                        # Controles del carrusel solo si hay múltiples imágenes
                        if total_imagenes > 1:
                            st.markdown("### 🖼️ Galería de Fotos")
                            
                            # Selectbox elegante con labels personalizados
                            opciones_imagenes = [f"📸 Imagen {j+1}" for j in range(total_imagenes)]
                            imagen_seleccionada_option = st.selectbox(
                                "Seleccionar imagen:",
                                options=opciones_imagenes,
                                index=indice,
                                key=f"select_{receta['id']}",
                                help="Elige la imagen a mostrar",
                                on_change=mantener_expander_abierto,
                                kwargs={"clave_estado": expander_state_key}
                            )
                            
                            # Actualizar índice basado en la selección
                            indice = opciones_imagenes.index(imagen_seleccionada_option)
                            st.session_state[carousel_key] = indice
                            st.session_state[expander_state_key] = True
                            
                            st.markdown("---")
                        
                        imagen_seleccionada = imagenes_receta[indice]
                        autor = imagen_seleccionada.get('autor') or "Autor desconocido"
                        
                        # Mostrar imagen con mejor formato
                        st.image(
                            imagen_seleccionada.get('url'),
                            caption=f"📸 Autor: {autor} | 📍 {indice + 1} de {total_imagenes}",
                            width='stretch'
                        )
                        
                        if st.button("🗑️ Eliminar imagen", key=f"delete_image_{i}_{indice}"):
                            imagenes_actualizadas = [img for img in imagenes_receta if img != imagen_seleccionada]
                            datos_actualizacion = {
                                'imagenes': imagenes_actualizadas,
                                'tiene_foto': len(imagenes_actualizadas) > 0
                            }
                            
                            # Si no quedan imágenes, quitar url_imagen
                            if not imagenes_actualizadas:
                                datos_actualizacion['url_imagen'] = None
                            # Si se eliminó la primera imagen, actualizar url_imagen
                            elif receta.get('url_imagen') and imagen_seleccionada.get('url') == receta['url_imagen']:
                                datos_actualizacion['url_imagen'] = imagenes_actualizadas[0].get('url') if imagenes_actualizadas else None
                            
                            st.session_state[expander_state_key] = True

                            if supabase_manager.actualizar_receta(receta['id'], datos_actualizacion):
                                st.success("Imagen eliminada")
                                st.rerun()
                            else:
                                st.error("Error eliminando imagen")
                    elif receta.get('tiene_foto'):
                        st.info("📷 Foto pendiente")
                    else:
                        st.info("📷 Sin foto")
                    
                    # Subir nueva imagen - ABAJO
                    st.subheader("📸 Subir Foto")
                    nuevas_imagenes = st.file_uploader(
                        "Seleccionar imágenes",
                        type=['jpg', 'jpeg', 'png'],
                        accept_multiple_files=True,
                        key=f"upload_{i}_{st.session_state[f'upload_key_{i}']}"
                    )

                    autores_imagenes = []
                    if nuevas_imagenes:
                        st.caption("✍️ Indica el autor de cada imagen")
                        for idx, archivo in enumerate(nuevas_imagenes):
                            autor = st.text_input(
                                f"Autor para {archivo.name}",
                                key=f"autor_imagen_{i}_{idx}_{st.session_state[f'upload_key_{i}']}"
                            )
                            autores_imagenes.append(autor)

                        if st.button("Subir imágenes", key=f"upload_btn_{i}"):
                            imagenes_subidas = []
                            with st.spinner("Subiendo imágenes..."):
                                for idx, archivo in enumerate(nuevas_imagenes):
                                    archivo.seek(0)
                                    info_imagen = supabase_manager.subir_imagen(
                                        archivo.read(),
                                        archivo.name
                                    )

                                    if info_imagen:
                                        autor = (autores_imagenes[idx] or "Autor desconocido").strip()
                                        if not autor:
                                            autor = "Autor desconocido"

                                        info_imagen['autor'] = autor
                                        info_imagen['uploaded_at'] = datetime.utcnow().isoformat()
                                        imagenes_subidas.append(info_imagen)
                                    else:
                                        st.error(f"Error subiendo la imagen {archivo.name}")

                            if imagenes_subidas:
                                imagenes_actualizadas = (receta.get('imagenes') or []) + imagenes_subidas
                                datos_actualizacion = {
                                    'imagenes': imagenes_actualizadas,
                                    'tiene_foto': True
                                }

                                # Mantener compatibilidad con url_imagen para la primera imagen
                                if not receta.get('url_imagen') and imagenes_actualizadas:
                                    datos_actualizacion['url_imagen'] = imagenes_actualizadas[0].get('url')

                                st.session_state[expander_state_key] = True

                                if supabase_manager.actualizar_receta(receta['id'], datos_actualizacion):
                                    st.success("Imágenes subidas correctamente")
                                    st.session_state[f'upload_key_{i}'] += 1  # Resetear formulario
                                    st.rerun()
                                else:
                                    st.error("Error actualizando la receta")
                elif supabase_manager.imagenes_habilitadas():
                    st.info("📷 Módulo de imágenes desactivado")
                else:
                    st.info("📷 Módulo de imágenes no disponible")
            
            # Botones de acción
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button(f"✏️ Editar", key=f"edit_{i}"):
                    st.session_state[expander_state_key] = True
                    st.session_state[f'editando_{i}'] = True
            
            with col_btn2:
                if st.button(f"🗑️ Eliminar", key=f"delete_{i}"):
                    st.session_state[expander_state_key] = True
                    if supabase_manager.eliminar_receta(receta['id']):
                        st.success("Receta eliminada")
                        st.rerun()
                    else:
                        st.error("Error eliminando receta")
            
            # Formulario de edición
            if st.session_state.get(f'editando_{i}', False):
                st.markdown("---")
                st.subheader("✏️ Editar Receta")
                
                with st.form(f"form_edit_{i}"):
                    nuevo_creador = st.text_input(
                        "Nombre del creador",
                        value=receta['creador'],
                        key=f"creador_{i}",
                        help="Cambia el nombre del creador para unificar autores con nombres diferentes"
                    )
                    
                    nuevo_nombre = st.text_input(
                        "Nombre de la receta",
                        value=receta.get('nombre_receta', ''),
                        key=f"nombre_{i}"
                    )
                    
                    nuevos_ingredientes = st.text_area(
                        "Ingredientes",
                        value=receta.get('ingredientes', ''),
                        height=100,
                        key=f"ingredientes_{i}"
                    )
                    
                    nuevos_pasos = st.text_area(
                        "Pasos de preparación",
                        value=receta.get('pasos_preparacion', ''),
                        height=100,
                        key=f"pasos_{i}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    
                    with col_save:
                        if st.form_submit_button("💾 Guardar"):
                            datos_actualizacion = {
                                'creador': nuevo_creador,
                                'nombre_receta': nuevo_nombre if nuevo_nombre else None,
                                'ingredientes': nuevos_ingredientes,
                                'pasos_preparacion': nuevos_pasos if nuevos_pasos else None
                            }
                            
                            if supabase_manager.actualizar_receta(receta['id'], datos_actualizacion):
                                st.session_state[expander_state_key] = True
                                st.success("Receta actualizada")
                                st.session_state[f'editando_{i}'] = False
                                st.rerun()
                            else:
                                st.error("Error actualizando receta")
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state[f'editando_{i}'] = False
                            st.session_state[expander_state_key] = False
                            st.rerun()
            
            st.markdown("---")


if __name__ == "__main__":
    main()
