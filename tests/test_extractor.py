"""
Tests para extractor.py
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from src.recetario_whatsapp.extractor import WhatsAppExtractor


class TestWhatsAppExtractor:
    """Tests para la clase WhatsAppExtractor."""
    
    def test_init(self, mock_env_vars):
        """Test inicialización del extractor."""
        with patch('src.recetario_whatsapp.extractor.MistralClient') as mock_mistral, \
             patch('src.recetario_whatsapp.extractor.SupabaseManager') as mock_supabase:
            
            extractor = WhatsAppExtractor()
            
            assert extractor.mistral_client is not None
            assert extractor.supabase_manager is not None
    
    def test_parsear_mensajes_formato_principal(self, mock_env_vars):
        """Test parseo de mensajes con formato principal."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            contenido = """[01/10/25, 18:02:12] Ana: Hola mundo
[02/10/25, 19:30:45] Luis: ¿Cómo estás?"""
            
            mensajes = extractor._parsear_mensajes(contenido)
            
            assert len(mensajes) == 2
            assert mensajes[0]['creador'] == 'Ana'
            assert mensajes[0]['mensaje'] == 'Hola mundo'
            assert mensajes[1]['creador'] == 'Luis'
            assert mensajes[1]['mensaje'] == '¿Cómo estás?'
    
    def test_parsear_mensajes_formato_alternativo(self, mock_env_vars):
        """Test parseo de mensajes con formato alternativo."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            contenido = """01/10/25, 18:02 - Ana: Hola mundo
02/10/25, 19:30 - Luis: ¿Cómo estás?"""
            
            mensajes = extractor._parsear_mensajes(contenido)
            
            assert len(mensajes) == 2
            assert mensajes[0]['creador'] == 'Ana'
            assert mensajes[0]['mensaje'] == 'Hola mundo'
            assert mensajes[1]['creador'] == 'Luis'
            assert mensajes[1]['mensaje'] == '¿Cómo estás?'
    
    def test_parsear_mensajes_vacios(self, mock_env_vars):
        """Test parseo con líneas vacías."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            contenido = """[01/10/25, 18:02:12] Ana: Hola mundo

[02/10/25, 19:30:45] Luis: ¿Cómo estás?
"""
            
            mensajes = extractor._parsear_mensajes(contenido)
            
            assert len(mensajes) == 2
            assert mensajes[0]['creador'] == 'Ana'
            assert mensajes[1]['creador'] == 'Luis'
    
    def test_filtrar_por_fecha(self, mock_env_vars):
        """Test filtrado por fecha."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            mensajes = [
                {'fecha': '01/10/25 18:02:12', 'creador': 'Ana', 'mensaje': 'Mensaje 1'},
                {'fecha': '15/10/25 19:30:45', 'creador': 'Luis', 'mensaje': 'Mensaje 2'},
                {'fecha': '20/10/25 20:15:30', 'creador': 'Marta', 'mensaje': 'Mensaje 3'}
            ]
            
            resultado = extractor._filtrar_por_fecha(mensajes, '2025-10-10')
            
            assert len(resultado) == 2
            assert resultado[0]['creador'] == 'Luis'
            assert resultado[1]['creador'] == 'Marta'
    
    def test_filtrar_por_fecha_formato_invalido(self, mock_env_vars):
        """Test filtrado con formato de fecha inválido."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            mensajes = [
                {'fecha': 'fecha_invalida', 'creador': 'Ana', 'mensaje': 'Mensaje 1'}
            ]
            
            resultado = extractor._filtrar_por_fecha(mensajes, '2025-10-10')
            
            # Debe incluir el mensaje aunque no se pueda parsear la fecha
            assert len(resultado) == 1
            assert resultado[0]['creador'] == 'Ana'
    
    def test_agrupar_mensajes_consecutivos(self, mock_env_vars):
        """Test agrupación de mensajes consecutivos."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            mensajes = [
                {'fecha': '01/10/25 18:02:12', 'creador': 'Ana', 'mensaje': 'Mensaje 1'},
                {'fecha': '01/10/25 18:02:13', 'creador': 'Ana', 'mensaje': 'Mensaje 2'},
                {'fecha': '01/10/25 18:05:00', 'creador': 'Luis', 'mensaje': 'Mensaje 3'},
                {'fecha': '01/10/25 18:05:01', 'creador': 'Luis', 'mensaje': 'Mensaje 4'}
            ]
            
            bloques = extractor._agrupar_mensajes_consecutivos(mensajes)
            
            assert len(bloques) == 2
            assert bloques[0]['creador'] == 'Ana'
            assert 'Mensaje 1\nMensaje 2' in bloques[0]['texto']
            assert bloques[1]['creador'] == 'Luis'
            assert 'Mensaje 3\nMensaje 4' in bloques[1]['texto']
    
    def test_agrupar_mensajes_vacios(self, mock_env_vars):
        """Test agrupación con lista vacía."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            bloques = extractor._agrupar_mensajes_consecutivos([])
            
            assert bloques == []
    
    def test_es_candidato_receta_con_palabras_clave(self, mock_env_vars):
        """Test detección de candidato con palabras clave."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            
            # Casos positivos
            assert extractor._es_candidato_receta("Ingredientes: harina, azúcar")
            assert extractor._es_candidato_receta("Receta de tarta")
            assert extractor._es_candidato_receta("Pasos de preparación")
            
            # Casos negativos
            assert not extractor._es_candidato_receta("Hola, ¿cómo estás?")
            assert not extractor._es_candidato_receta("")
    
    def test_es_candidato_receta_con_patrones_lista(self, mock_env_vars):
        """Test detección de candidato con patrones de lista."""
        with patch('src.recetario_whatsapp.extractor.MistralClient'), \
             patch('src.recetario_whatsapp.extractor.SupabaseManager'):
            
            extractor = WhatsAppExtractor()
            
            # Casos positivos
            assert extractor._es_candidato_receta("- 200 g harina")
            assert extractor._es_candidato_receta("• 1 taza de azúcar")
            assert extractor._es_candidato_receta("2 huevos grandes")
            assert extractor._es_candidato_receta("300 g de pasta")
            
            # Casos negativos
            assert not extractor._es_candidato_receta("Hola mundo")
            assert not extractor._es_candidato_receta("123456789")
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_procesar_archivo_success(self, mock_supabase, mock_mistral, mock_env_vars, sample_whatsapp_text, mock_mistral_response):
        """Test procesamiento exitoso de archivo."""
        # Configurar mocks
        mock_mistral_instance = Mock()
        mock_mistral_instance.extraer_receta.return_value = mock_mistral_response
        mock_mistral.return_value = mock_mistral_instance
        
        mock_supabase_instance = Mock()
        mock_supabase_instance.insertar_receta.return_value = {'id': 1}
        mock_supabase.return_value = mock_supabase_instance
        
        # Crear archivo temporal
        with patch('builtins.open', mock_open(read_data=sample_whatsapp_text)):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        assert resultado['mensajes_procesados'] > 0
        assert resultado['recetas_extraidas'] > 0
        assert resultado['recetas_insertadas'] > 0
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_procesar_archivo_error_lectura(self, mock_supabase, mock_mistral, mock_env_vars):
        """Test procesamiento con error de lectura."""
        mock_mistral.return_value = Mock()
        mock_supabase.return_value = Mock()
        
        with patch('builtins.open', side_effect=IOError("Error de lectura")):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        assert 'error' in resultado
        assert 'Error leyendo archivo' in resultado['error']
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_procesar_archivo_no_receta(self, mock_supabase, mock_mistral, mock_env_vars):
        """Test procesamiento cuando no hay recetas."""
        # Configurar mocks
        mock_mistral_instance = Mock()
        mock_mistral_instance.extraer_receta.return_value = {'es_receta': False}
        mock_mistral.return_value = mock_mistral_instance
        
        mock_supabase_instance = Mock()
        mock_supabase.return_value = mock_supabase_instance
        
        contenido = """[01/10/25, 18:02:12] Ana: Hola mundo
[01/10/25, 18:05:00] Luis: ¿Cómo estás?"""
        
        with patch('builtins.open', mock_open(read_data=contenido)):
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('test.txt')
        
        assert resultado['recetas_extraidas'] == 0
        assert resultado['recetas_insertadas'] == 0
    
    @patch('src.recetario_whatsapp.extractor.MistralClient')
    @patch('src.recetario_whatsapp.extractor.SupabaseManager')
    def test_actualizar_estado_procesamiento(self, mock_supabase, mock_mistral, mock_env_vars):
        """Test actualización del estado de procesamiento."""
        mock_mistral.return_value = Mock()
        mock_supabase.return_value = Mock()
        
        with patch('builtins.open', mock_open()), \
             patch('os.makedirs') as mock_makedirs:
            
            extractor = WhatsAppExtractor()
            extractor._actualizar_estado_procesamiento('2025-10-12T14:21:32+02:00')
            
            mock_makedirs.assert_called_once_with('state', exist_ok=True)
    
    def test_main_function(self, mock_env_vars):
        """Test función main del módulo."""
        with patch('src.recetario_whatsapp.extractor.argparse.ArgumentParser') as mock_parser, \
             patch('src.recetario_whatsapp.extractor.load_dotenv') as mock_dotenv, \
             patch('src.recetario_whatsapp.extractor.WhatsAppExtractor') as mock_extractor_class:
            
            # Configurar mocks
            mock_args = Mock()
            mock_args.file = 'test.txt'
            mock_args.desde = None
            mock_parser.return_value.parse_args.return_value = mock_args
            
            mock_extractor = Mock()
            mock_extractor.procesar_archivo.return_value = {'recetas_insertadas': 1}
            mock_extractor_class.return_value = mock_extractor
            
            # Importar y ejecutar main
            from src.recetario_whatsapp.extractor import main
            main()
            
            mock_dotenv.assert_called_once()
            mock_extractor.procesar_archivo.assert_called_once_with('test.txt', None)
