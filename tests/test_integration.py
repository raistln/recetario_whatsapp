"""
Tests de integración para el sistema completo.
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from src.recetario_whatsapp.extractor import WhatsAppExtractor
from src.recetario_whatsapp.mistral_client import MistralClient
from src.recetario_whatsapp.supabase_utils import SupabaseManager


class TestIntegration:
    """Tests de integración del sistema completo."""
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_full_workflow(self, mock_supabase_class, mock_mistral_class, mock_env_vars):
        """Test del flujo completo de procesamiento."""
        # Configurar mocks
        mock_mistral = Mock()
        mock_mistral.extraer_receta.return_value = {
            "es_receta": True,
            "creador": "Ana",
            "nombre_receta": "Tarta de queso",
            "ingredientes": "- 200 g harina\n- 100 g azúcar",
            "pasos_preparacion": "1. Mezclar todo.\n2. Hornear 30 min.",
            "tiene_foto": False,
            "fecha_mensaje": "2025-10-12T14:21:32+02:00"
        }
        mock_mistral_class.return_value = mock_mistral
        
        mock_supabase = Mock()
        mock_supabase.insertar_receta.return_value = {'id': 1}
        mock_supabase_class.return_value = mock_supabase
        
        # Contenido de WhatsApp de prueba
        whatsapp_content = """[01/10/25, 18:02:12] Ana: ¡Probar esta receta!
[01/10/25, 18:02:13] Ana: Ingredientes:
- 200 g harina
- 100 g azúcar
- 2 huevos
Pasos:
1. Mezclar todo.
2. Hornear 30 minutos.
[01/10/25, 18:05:00] Luis: jaja qué guay"""
        
        # Ejecutar el flujo completo
        with patch('builtins.open', mock_open(read_data=whatsapp_content)):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        # Verificar resultados
        assert resultado['mensajes_procesados'] > 0
        assert resultado['recetas_extraidas'] > 0
        assert resultado['recetas_insertadas'] > 0
        
        # Verificar que se llamaron los métodos esperados
        mock_mistral.extraer_receta.assert_called()
        mock_supabase.insertar_receta.assert_called()
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_error_handling_workflow(self, mock_supabase_class, mock_mistral_class, mock_env_vars):
        """Test del manejo de errores en el flujo completo."""
        # Configurar mocks con errores
        mock_mistral = Mock()
        mock_mistral.extraer_receta.side_effect = Exception("Error de API")
        mock_mistral_class.return_value = mock_mistral
        
        mock_supabase = Mock()
        mock_supabase_class.return_value = mock_supabase
        
        # Contenido de WhatsApp de prueba
        whatsapp_content = """[01/10/25, 18:02:12] Ana: Ingredientes:
- 200 g harina
- 100 g azúcar"""
        
        # Ejecutar el flujo con errores
        with patch('builtins.open', mock_open(read_data=whatsapp_content)):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        # Verificar que se manejó el error correctamente
        assert resultado['recetas_extraidas'] == 0
        assert resultado['recetas_insertadas'] == 0
    
    def test_whatsapp_parsing_edge_cases(self, mock_env_vars):
        """Test casos edge del parsing de WhatsApp."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            
            # Test con diferentes formatos de fecha
            contenido = """[01/10/25, 18:02:12] Ana: Mensaje 1
01/10/25, 18:02 - Luis: Mensaje 2
[01/10/25, 18:02:12] Ana: Mensaje 3"""
            
            mensajes = extractor._parsear_mensajes(contenido)
            assert len(mensajes) == 3
            assert mensajes[0]['creador'] == 'Ana'
            assert mensajes[1]['creador'] == 'Luis'
            assert mensajes[2]['creador'] == 'Ana'
    
    def test_recipe_detection_edge_cases(self, mock_env_vars):
        """Test casos edge de detección de recetas."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            
            # Casos que deberían ser candidatos
            assert extractor._es_candidato_receta("Ingredientes:\n- 200g harina")
            assert extractor._es_candidato_receta("Receta de tarta")
            assert extractor._es_candidato_receta("Pasos:\n1. Mezclar")
            assert extractor._es_candidato_receta("- 1 taza de azúcar")
            assert extractor._es_candidato_receta("• 2 huevos")
            assert extractor._es_candidato_receta("300 g de pasta")
            
            # Casos que NO deberían ser candidatos
            assert not extractor._es_candidato_receta("Hola, ¿cómo estás?")
            assert not extractor._es_candidato_receta("")
            assert not extractor._es_candidato_receta("123456789")
            assert not extractor._es_candidato_receta("Solo texto normal")
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_incremental_processing(self, mock_supabase_class, mock_mistral_class, mock_env_vars):
        """Test procesamiento incremental con filtro de fecha."""
        # Configurar mocks
        mock_mistral = Mock()
        mock_mistral.extraer_receta.return_value = {"es_receta": False}
        mock_mistral_class.return_value = mock_mistral
        
        mock_supabase = Mock()
        mock_supabase_class.return_value = mock_supabase
        
        # Contenido con fechas diferentes
        whatsapp_content = """[01/10/25, 18:02:12] Ana: Mensaje antiguo
[15/10/25, 18:02:13] Ana: Ingredientes:
- 200 g harina
- 100 g azúcar
[20/10/25, 18:05:00] Luis: Mensaje reciente"""
        
        with patch('builtins.open', mock_open(read_data=whatsapp_content)):
            extractor = WhatsAppExtractor()
            
            # Procesar solo desde el 10 de octubre
            resultado = extractor.procesar_archivo('test.txt', '2025-10-10')
            
            # Verificar que se procesaron solo los mensajes recientes
            assert resultado['mensajes_procesados'] > 0
    
    def test_state_management(self, mock_env_vars):
        """Test manejo del estado de procesamiento."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'), \
             patch('builtins.open', mock_open()), \
             patch('os.makedirs') as mock_makedirs:
            
            extractor = WhatsAppExtractor()
            
            # Test actualización de estado
            extractor._actualizar_estado_procesamiento('2025-10-12T14:21:32+02:00')
            
            # Verificar que se creó el directorio
            mock_makedirs.assert_called_with('state', exist_ok=True)
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_multiple_recipes_in_conversation(self, mock_supabase_class, mock_mistral_class, mock_env_vars):
        """Test procesamiento de múltiples recetas en una conversación."""
        # Configurar mocks
        mock_mistral = Mock()
        mock_mistral.extraer_receta.side_effect = [
            {
                "es_receta": True,
                "creador": "Ana",
                "nombre_receta": "Tarta de queso",
                "ingredientes": "- 200 g harina",
                "pasos_preparacion": "1. Mezclar",
                "tiene_foto": False,
                "fecha_mensaje": "2025-10-12T14:21:32+02:00"
            },
            {
                "es_receta": True,
                "creador": "Luis",
                "nombre_receta": "Gazpacho",
                "ingredientes": "- 1 kg tomates",
                "pasos_preparacion": "Triturar",
                "tiene_foto": True,
                "fecha_mensaje": "2025-10-12T15:21:32+02:00"
            }
        ]
        mock_mistral_class.return_value = mock_mistral
        
        mock_supabase = Mock()
        mock_supabase.insertar_receta.return_value = {'id': 1}
        mock_supabase_class.return_value = mock_supabase
        
        # Contenido con múltiples recetas
        whatsapp_content = """[01/10/25, 18:02:12] Ana: Ingredientes:
- 200 g harina
Pasos:
1. Mezclar
[01/10/25, 18:05:00] Luis: jaja qué guay
[01/10/25, 19:02:12] Luis: Ingredientes:
- 1 kg tomates
Pasos:
Triturar
<adjunto: imagen excluida>"""
        
        with patch('builtins.open', mock_open(read_data=whatsapp_content)):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        # Verificar que se procesaron múltiples recetas
        assert resultado['recetas_extraidas'] == 2
        assert resultado['recetas_insertadas'] == 2
        assert mock_mistral.extraer_receta.call_count == 2
        assert mock_supabase.insertar_receta.call_count == 2

