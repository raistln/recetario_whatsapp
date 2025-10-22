"""
Tests para mistral_client.py
"""
import pytest
import json
from unittest.mock import Mock, patch
from src.recetario_whatsapp.mistral_client import MistralClient


class TestMistralClient:
    """Tests para la clase MistralClient."""
    
    def test_init_success(self, mock_env_vars):
        """Test inicialización exitosa del cliente."""
        with patch('src.recetario_whatsapp.mistral_client.Mistral') as mock_mistral:
            client = MistralClient()
            assert client.model == "mistral-small-latest"
            mock_mistral.assert_called_once_with(api_key='test_mistral_key')
    
    def test_init_missing_api_key(self):
        """Test inicialización sin API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="MISTRAL_API_KEY no encontrada"):
                MistralClient()
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_extraer_receta_success(self, mock_mistral_class, mock_env_vars, mock_mistral_response):
        """Test extracción exitosa de receta."""
        # Configurar mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_mistral_response)
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_class.return_value = mock_client
        
        client = MistralClient()
        resultado = client.extraer_receta("texto de prueba")
        
        assert resultado == mock_mistral_response
        mock_client.chat.complete.assert_called_once()
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_extraer_receta_invalid_json(self, mock_mistral_class, mock_env_vars):
        """Test extracción con JSON inválido."""
        # Configurar mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "respuesta no válida"
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_class.return_value = mock_client
        
        client = MistralClient()
        resultado = client.extraer_receta("texto de prueba")
        
        assert resultado["es_receta"] is False
        assert "error" in resultado
        assert "Respuesta no válida" in resultado["error"]
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_extraer_receta_api_error(self, mock_mistral_class, mock_env_vars):
        """Test extracción con error de API."""
        # Configurar mock
        mock_client = Mock()
        mock_client.chat.complete.side_effect = Exception("Error de API")
        mock_mistral_class.return_value = mock_client
        
        client = MistralClient()
        resultado = client.extraer_receta("texto de prueba")
        
        assert resultado["es_receta"] is False
        assert "Error en la API de Mistral" in resultado["error"]
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_crear_prompt_extraccion(self, mock_mistral_class, mock_env_vars):
        """Test creación del prompt de extracción."""
        mock_mistral_class.return_value = Mock()
        client = MistralClient()
        prompt = client._crear_prompt_extraccion()
        
        assert "extractor automático de recetas" in prompt
        assert "REGLAS:" in prompt
        assert "Ejemplo de Entrada" in prompt
        assert "Ejemplo de Salida" in prompt
        assert "JSON" in prompt
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_extraer_receta_no_receta(self, mock_mistral_class, mock_env_vars):
        """Test extracción cuando no es una receta."""
        # Configurar mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"es_receta": false}'
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_class.return_value = mock_client
        
        client = MistralClient()
        resultado = client.extraer_receta("texto que no es receta")
        
        assert resultado["es_receta"] is False
    
    @patch('src.recetario_whatsapp.mistral_client.Mistral')
    def test_extraer_receta_with_photo(self, mock_mistral_class, mock_env_vars):
        """Test extracción de receta con foto."""
        receta_con_foto = {
            "es_receta": True,
            "creador": "Marta",
            "nombre_receta": "Gazpacho",
            "ingredientes": "- 1 kg tomates",
            "pasos_preparacion": "Triturar y refrigerar",
            "tiene_foto": True,
            "fecha_mensaje": "2025-10-12T14:21:32+02:00"
        }
        
        # Configurar mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(receta_con_foto)
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_class.return_value = mock_client
        
        client = MistralClient()
        resultado = client.extraer_receta("texto con <adjunto: imagen excluida>")
        
        assert resultado["tiene_foto"] is True
        assert resultado["es_receta"] is True
