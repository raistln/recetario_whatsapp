"""
Tests para supabase_utils.py
"""
import pytest
from unittest.mock import Mock, patch
from src.recetario_whatsapp.supabase_utils import SupabaseManager


class TestSupabaseManager:
    """Tests para la clase SupabaseManager."""
    
    def test_init_success(self, mock_env_vars):
        """Test inicialización exitosa del manager."""
        with patch('src.recetario_whatsapp.supabase_utils.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            manager = SupabaseManager()
            
            assert manager.client == mock_client
            assert manager.storage_bucket == 'test-recetas'
            mock_create.assert_called_once_with('https://test.supabase.co', 'test_supabase_key')
    
    def test_init_missing_url(self):
        """Test inicialización sin URL de Supabase."""
        with patch.dict('os.environ', {'SUPABASE_KEY': 'test'}, clear=True):
            with pytest.raises(ValueError, match="SUPABASE_URL y SUPABASE_KEY deben estar configuradas"):
                SupabaseManager()
    
    def test_init_missing_key(self):
        """Test inicialización sin key de Supabase."""
        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co'}, clear=True):
            with pytest.raises(ValueError, match="SUPABASE_URL y SUPABASE_KEY deben estar configuradas"):
                SupabaseManager()
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_insertar_receta_success(self, mock_create, mock_env_vars, sample_receta_data):
        """Test inserción exitosa de receta."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_receta_data]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.insertar_receta(sample_receta_data)
        
        assert resultado == sample_receta_data
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_insertar_receta_error(self, mock_create, mock_env_vars, sample_receta_data):
        """Test inserción con error."""
        mock_client = Mock()
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.insertar_receta(sample_receta_data)
        
        assert resultado is None
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_obtener_recetas_success(self, mock_create, mock_env_vars, sample_receta_data):
        """Test obtención exitosa de recetas."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_receta_data]
        mock_client.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.obtener_recetas()
        
        assert resultado == [sample_receta_data]
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_obtener_recetas_con_filtro(self, mock_create, mock_env_vars, sample_receta_data):
        """Test obtención de recetas con filtro de creador."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_receta_data]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.obtener_recetas("Ana")
        
        assert resultado == [sample_receta_data]
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_obtener_recetas_error(self, mock_create, mock_env_vars):
        """Test obtención de recetas con error."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.obtener_recetas()
        
        assert resultado == []
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_buscar_recetas_success(self, mock_create, mock_env_vars, sample_receta_data):
        """Test búsqueda exitosa de recetas."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_receta_data]
        mock_client.table.return_value.select.return_value.or_.return_value.order.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.buscar_recetas("harina")
        
        assert resultado == [sample_receta_data]
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_buscar_recetas_error(self, mock_create, mock_env_vars):
        """Test búsqueda con error."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.or_.return_value.order.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.buscar_recetas("harina")
        
        assert resultado == []
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_actualizar_receta_success(self, mock_create, mock_env_vars):
        """Test actualización exitosa de receta."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{'id': 1}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.actualizar_receta(1, {'nombre_receta': 'Nuevo nombre'})
        
        assert resultado is True
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_actualizar_receta_error(self, mock_create, mock_env_vars):
        """Test actualización con error."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.actualizar_receta(1, {'nombre_receta': 'Nuevo nombre'})
        
        assert resultado is False
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_eliminar_receta_success(self, mock_create, mock_env_vars):
        """Test eliminación exitosa de receta."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{'id': 1}]
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.eliminar_receta(1)
        
        assert resultado is True
        mock_client.table.assert_called_once_with('recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_eliminar_receta_error(self, mock_create, mock_env_vars):
        """Test eliminación con error."""
        mock_client = Mock()
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.eliminar_receta(1)
        
        assert resultado is False
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_subir_imagen_success(self, mock_create, mock_env_vars):
        """Test subida exitosa de imagen."""
        mock_client = Mock()
        mock_client.storage.from_.return_value.upload.return_value = True
        mock_client.storage.from_.return_value.get_public_url.return_value = 'https://test.com/image.jpg'
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.subir_imagen(b'test image data', 'test.jpg')
        
        assert resultado == 'https://test.com/image.jpg'
        mock_client.storage.from_.assert_called_with('test-recetas')
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_subir_imagen_error(self, mock_create, mock_env_vars):
        """Test subida de imagen con error."""
        mock_client = Mock()
        mock_client.storage.from_.return_value.upload.side_effect = Exception("Error de storage")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.subir_imagen(b'test image data', 'test.jpg')
        
        assert resultado is None
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_obtener_creadores_unicos_success(self, mock_create, mock_env_vars):
        """Test obtención exitosa de creadores únicos."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            {'creador': 'Ana'},
            {'creador': 'Luis'},
            {'creador': 'Ana'},  # Duplicado
            {'creador': 'Marta'}
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.obtener_creadores_unicos()
        
        assert set(resultado) == {'Ana', 'Luis', 'Marta'}
        assert len(resultado) == 3  # Sin duplicados
    
    @patch('src.recetario_whatsapp.supabase_utils.create_client')
    def test_obtener_creadores_unicos_error(self, mock_create, mock_env_vars):
        """Test obtención de creadores con error."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.execute.side_effect = Exception("Error de DB")
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        resultado = manager.obtener_creadores_unicos()
        
        assert resultado == []
