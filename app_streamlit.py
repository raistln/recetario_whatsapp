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
        
        # Opción para desactivar imágenes
        imagenes_habilitadas = st.checkbox(
            "📷 Habilitar módulo de imágenes",
            value=False,
            help="Activa solo si quieres gestionar fotos de recetas"
        )
        
        # Botón para agregar receta manualmente
        st.markdown("---")
        st.header("➕ Agregar Receta")
        
        if st.button("📝 Crear Nueva Receta", type="primary"):
            st.session_state['mostrar_formulario_nueva'] = True
        
        # Botón para procesar nuevo archivo
        st.markdown("---")
        st.header("📁 Procesar Archivo")
        archivo_subido = st.file_uploader(
            "Subir archivo de WhatsApp",
            type=['txt'],
            help="Sube un archivo .txt exportado de WhatsApp"
        )
        
        if archivo_subido:
            if st.button("Procesar Archivo"):
                with st.spinner("Procesando archivo..."):
                    # Guardar archivo temporalmente
                    contenido = archivo_subido.read().decode('utf-8')
                    with open('temp_whatsapp.txt', 'w', encoding='utf-8') as f:
                        f.write(contenido)
                    
                    # Procesar archivo
                    resultado = extractor.procesar_archivo('temp_whatsapp.txt')
                    
                    # Limpiar archivo temporal
                    os.remove('temp_whatsapp.txt')
                    
                    st.success(f"Archivo procesado: {resultado.get('recetas_insertadas', 0)} recetas añadidas")
                    st.markdown("---")
    
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
        if imagenes_habilitadas:
            st.metric("Con Fotos", len([r for r in recetas if r.get('tiene_foto')]))
        else:
            st.metric("Módulo Imágenes", "Desactivado")
    
    st.markdown("---")
    
    # Mostrar recetas
    if not recetas:
        st.info("No se encontraron recetas. ¡Sube un archivo de WhatsApp para empezar!")
        return
    
    for i, receta in enumerate(recetas):
        with st.expander(f"🍽️ {receta.get('nombre_receta', 'Receta sin nombre')} - {receta['creador']}"):
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
                # Mostrar imagen solo si está habilitado
                if imagenes_habilitadas:
                    if receta.get('url_imagen'):
                        try:
                            st.image(receta['url_imagen'], caption="Foto de la receta")
                        except:
                            st.info("Error cargando imagen")
                    elif receta.get('tiene_foto'):
                        st.info("📷 Foto pendiente")
                    else:
                        st.info("📷 Sin foto")
                    
                    # Subir nueva imagen
                    st.subheader("📸 Subir Foto")
                    nueva_imagen = st.file_uploader(
                        "Seleccionar imagen",
                        type=['jpg', 'jpeg', 'png'],
                        key=f"upload_{i}"
                    )
                    
                    if nueva_imagen:
                        if st.button(f"Subir Imagen", key=f"upload_btn_{i}"):
                            with st.spinner("Subiendo imagen..."):
                                # Convertir a bytes
                                img_bytes = nueva_imagen.read()
                                
                                # Subir a Supabase
                                url_imagen = supabase_manager.subir_imagen(
                                    img_bytes, 
                                    nueva_imagen.name
                                )
                                
                                if url_imagen:
                                    # Actualizar receta
                                    if supabase_manager.actualizar_receta(
                                        receta['id'], 
                                        {'url_imagen': url_imagen, 'tiene_foto': True}
                                    ):
                                        st.success("Imagen subida correctamente")
                                        st.rerun()
                                    else:
                                        st.error("Error actualizando receta")
                                else:
                                    st.error("Error subiendo imagen")
                else:
                    st.info("📷 Módulo de imágenes desactivado")
            
            # Botones de acción
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button(f"✏️ Editar", key=f"edit_{i}"):
                    st.session_state[f'editando_{i}'] = True
            
            with col_btn2:
                if st.button(f"🗑️ Eliminar", key=f"delete_{i}"):
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
                                st.success("Receta actualizada")
                                st.session_state[f'editando_{i}'] = False
                                st.rerun()
                            else:
                                st.error("Error actualizando receta")
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state[f'editando_{i}'] = False
                            st.rerun()
            
            st.markdown("---")


if __name__ == "__main__":
    main()
