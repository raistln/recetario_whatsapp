"""
Tests para app.py (Streamlit)
"""
import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from src.recetario_whatsapp.app import get_supabase_manager, get_extractor, main


class TestStreamlitApp:
    """Tests para la aplicación Streamlit."""
    
    def test_get_supabase_manager_success(self, mock_env_vars):
        """Test obtención exitosa del gestor de Supabase."""
        with patch('src.recetario_whatsapp.app.SupabaseManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            resultado = get_supabase_manager()
            
            assert resultado == mock_manager
            mock_manager_class.assert_called_once()
    
    def test_get_supabase_manager_error(self, mock_env_vars):
        """Test obtención del gestor con error."""
        with patch('src.recetario_whatsapp.app.SupabaseManager', side_effect=Exception("Error de conexión")):
            resultado = get_supabase_manager()
            
            assert resultado is None
    
    def test_get_extractor_success(self, mock_env_vars):
        """Test obtención exitosa del extractor."""
        with patch('src.recetario_whatsapp.app.WhatsAppExtractor') as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            
            resultado = get_extractor()
            
            assert resultado == mock_extractor
            mock_extractor_class.assert_called_once()
    
    def test_get_extractor_error(self, mock_env_vars):
        """Test obtención del extractor con error."""
        with patch('src.recetario_whatsapp.app.WhatsAppExtractor', side_effect=Exception("Error de inicialización")):
            resultado = get_extractor()
            
            assert resultado is None
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_without_services(self, mock_st, mock_env_vars):
        """Test main sin servicios disponibles."""
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=None), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=None):
            
            main()
            
            mock_st.error.assert_called_with("No se pudieron inicializar los servicios necesarios. Verifica la configuración.")
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_services_no_recetas(self, mock_st, mock_env_vars):
        """Test main con servicios pero sin recetas."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = []
        mock_supabase.obtener_recetas.return_value = []
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.title.assert_called_with("🍳 Recetario WhatsApp")
            mock_st.sidebar.header.assert_called()
            mock_st.text_input.assert_called()
            mock_st.selectbox.assert_called()
            mock_st.file_uploader.assert_called()
            mock_st.info.assert_called_with("No se encontraron recetas. ¡Sube un archivo de WhatsApp para empezar!")
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_recetas(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con recetas disponibles."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana', 'Luis']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        mock_supabase.buscar_recetas.return_value = [sample_receta_data]
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_st.expander.return_value.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.return_value = False
            mock_st.file_uploader.return_value = None
            
            main()
            
            # Verificar que se llamaron los métodos esperados
            mock_st.title.assert_called_with("🍳 Recetario WhatsApp")
            mock_supabase.obtener_recetas.assert_called_once()
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_search_term(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con término de búsqueda."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana']
        mock_supabase.buscar_recetas.return_value = [sample_receta_data]
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_st.expander.return_value.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.return_value = False
            mock_st.file_uploader.return_value = None
            
            # Simular término de búsqueda
            mock_st.text_input.return_value = "harina"
            
            main()
            
            # Verificar que se llamó la búsqueda
            mock_supabase.buscar_recetas.assert_called_with("harina")
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_creator_filter(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con filtro de creador."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana', 'Luis']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_st.expander.return_value.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.return_value = False
            mock_st.file_uploader.return_value = None
            
            # Simular filtro de creador
            mock_st.text_input.return_value = ""  # Sin búsqueda
            mock_st.selectbox.return_value = "Ana"  # Filtro por Ana
            
            main()
            
            # Verificar que se llamó con el filtro de creador
            mock_supabase.obtener_recetas.assert_called_with("Ana")
    
    @patch('src.recetario_whatsapp.app.st')
    @patch('src.recetario_whatsapp.app.os')
    def test_main_with_file_upload(self, mock_os, mock_st, mock_env_vars, sample_receta_data):
        """Test main con subida de archivo."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        
        mock_extractor = Mock()
        mock_extractor.procesar_archivo.return_value = {'recetas_insertadas': 1}
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor), \
             patch('builtins.open', mock_open(read_data="test content")):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_st.expander.return_value.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.return_value = True  # Botón procesar presionado
            mock_st.file_uploader.return_value = Mock()  # Archivo subido
            mock_st.spinner.return_value.__enter__.return_value = None
            mock_st.success.return_value = None
            mock_st.rerun.return_value = None
            
            # Simular archivo subido
            mock_file = Mock()
            mock_file.read.return_value = b"test content"
            mock_st.file_uploader.return_value = mock_file
            
            main()
            
            # Verificar que se procesó el archivo
            mock_extractor.procesar_archivo.assert_called_once()
            mock_st.success.assert_called()
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_receta_editing(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con edición de receta."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        mock_supabase.actualizar_receta.return_value = True
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_expander = Mock()
            mock_st.expander.return_value = mock_expander
            mock_expander.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.return_value = True  # Botón editar presionado
            mock_st.file_uploader.return_value = None
            mock_st.form.return_value.__enter__.return_value = Mock()
            mock_st.text_input.return_value = "Nuevo nombre"
            mock_st.text_area.return_value = "Nuevos ingredientes"
            mock_st.form_submit_button.return_value = True  # Botón guardar presionado
            mock_st.success.return_value = None
            mock_st.rerun.return_value = None
            
            # Simular estado de edición
            mock_st.session_state = {'editando_0': True}
            
            main()
            
            # Verificar que se actualizó la receta
            mock_supabase.actualizar_receta.assert_called()
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_receta_deletion(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con eliminación de receta."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        mock_supabase.eliminar_receta.return_value = True
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_expander = Mock()
            mock_st.expander.return_value = mock_expander
            mock_expander.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.side_effect = [False, True]  # Botón eliminar presionado
            mock_st.file_uploader.return_value = None
            mock_st.success.return_value = None
            mock_st.rerun.return_value = None
            
            main()
            
            # Verificar que se eliminó la receta
            mock_supabase.eliminar_receta.assert_called_with(sample_receta_data['id'])
            mock_st.success.assert_called_with("Receta eliminada")
    
    @patch('src.recetario_whatsapp.app.st')
    def test_main_with_image_upload(self, mock_st, mock_env_vars, sample_receta_data):
        """Test main con subida de imagen."""
        # Configurar mocks
        mock_supabase = Mock()
        mock_supabase.obtener_creadores_unicos.return_value = ['Ana']
        mock_supabase.obtener_recetas.return_value = [sample_receta_data]
        mock_supabase.subir_imagen.return_value = 'https://test.com/image.jpg'
        mock_supabase.actualizar_receta.return_value = True
        
        mock_extractor = Mock()
        
        with patch('src.recetario_whatsapp.app.get_supabase_manager', return_value=mock_supabase), \
             patch('src.recetario_whatsapp.app.get_extractor', return_value=mock_extractor):
            
            # Mock de los elementos de Streamlit
            mock_st.columns.return_value = [Mock(), Mock(), Mock()]
            mock_st.metric.return_value = None
            mock_expander = Mock()
            mock_st.expander.return_value = mock_expander
            mock_expander.__enter__.return_value = Mock()
            mock_st.subheader.return_value = None
            mock_st.text.return_value = None
            mock_st.caption.return_value = None
            mock_st.info.return_value = None
            mock_st.button.side_effect = [False, False, True]  # Botón subir imagen presionado
            mock_st.file_uploader.return_value = Mock()  # Imagen subida
            mock_st.spinner.return_value.__enter__.return_value = None
            mock_st.success.return_value = None
            mock_st.rerun.return_value = None
            
            # Simular imagen subida
            mock_image = Mock()
            mock_image.read.return_value = b"image data"
            mock_image.name = "test.jpg"
            mock_st.file_uploader.return_value = mock_image
            
            main()
            
            # Verificar que se subió la imagen
            mock_supabase.subir_imagen.assert_called_with(b"image data", "test.jpg")
            mock_supabase.actualizar_receta.assert_called()


def mock_open(read_data=""):
    """Helper para mock de open."""
    from unittest.mock import mock_open as original_mock_open
    return original_mock_open(read_data=read_data)
