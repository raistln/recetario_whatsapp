"""
Configuración global de pytest para el proyecto recetario-whatsapp.
"""
import os
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Cargar variables de entorno de test
load_dotenv('.env.test', override=True)

@pytest.fixture
def mock_env_vars():
    """Fixture para variables de entorno de prueba."""
    env_vars = {
        'MISTRAL_API_KEY': 'test_mistral_key',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test_supabase_key',
        'SUPABASE_STORAGE_BUCKET': 'test-recetas'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_mistral_response():
    """Fixture para respuesta mock de Mistral."""
    return {
        "es_receta": True,
        "creador": "Ana",
        "nombre_receta": "Tarta de queso",
        "ingredientes": "- 200 g harina\n- 100 g azúcar",
        "pasos_preparacion": "1. Mezclar todo.\n2. Hornear 30 min.",
        "tiene_foto": False,
        "fecha_mensaje": "2025-10-12T14:21:32+02:00"
    }

@pytest.fixture
def sample_whatsapp_text():
    """Fixture con texto de ejemplo de WhatsApp."""
    return """[01/10/25, 18:02:12] Ana: ¡Probar esta receta!
[01/10/25, 18:02:13] Ana: Ingredientes:
- 200 g harina
- 100 g azúcar
- 2 huevos
Pasos:
1. Mezclar todo.
2. Hornear 30 minutos.
[01/10/25, 18:05:00] Luis: jaja qué guay"""

@pytest.fixture
def sample_receta_data():
    """Fixture con datos de receta de ejemplo."""
    return {
        'id': 1,
        'creador': 'Ana',
        'nombre_receta': 'Tarta de queso',
        'ingredientes': '- 200 g harina\n- 100 g azúcar',
        'pasos_preparacion': '1. Mezclar todo.\n2. Hornear 30 min.',
        'tiene_foto': False,
        'url_imagen': None,
        'fecha_mensaje': '2025-10-12T14:21:32+02:00'
    }

@pytest.fixture
def mock_supabase_client():
    """Fixture para cliente mock de Supabase."""
    mock_client = Mock()
    mock_client.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [{'id': 1}]
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{'id': 1}]
    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{'id': 1}]
    mock_client.storage.from_.return_value.upload.return_value = True
    mock_client.storage.from_.return_value.get_public_url.return_value = 'https://test.com/image.jpg'
    return mock_client
