"""Tests actualizados para `extractor.py`."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.recetario_whatsapp.extractor import WhatsAppExtractor


@pytest.fixture
def extractor(mock_env_vars):
    """Crea un extractor con dependencias mockeadas."""

    with (
        patch("src.recetario_whatsapp.extractor.MistralClient") as mistral_cls,
        patch("src.recetario_whatsapp.extractor.SupabaseManager") as supabase_cls,
    ):
        mistral_instance = MagicMock()
        supabase_instance = MagicMock()
        mistral_cls.return_value = mistral_instance
        supabase_cls.return_value = supabase_instance

        yield WhatsAppExtractor(), mistral_instance, supabase_instance


def test_parsear_mensajes_acepta_formatos_varios(extractor):
    extractor_obj, _, _ = extractor
    contenido = """[01/10/25, 18:02:12] Ana: Hola mundo
01/10/25, 18:03 - Luis: ¡Hola!
[01/10/25, 18:05:44] Ana: Seguimos"""

    mensajes = extractor_obj._parsear_mensajes(contenido)

    autores = [m["creador"] for m in mensajes]
    assert autores == ["Ana", "Luis", "Ana"]
    assert mensajes[0]["mensaje"] == "Hola mundo"
    assert mensajes[1]["mensaje"] == "¡Hola!"


def test_filtrar_por_fecha_descarta_antiguos(extractor):
    extractor_obj, _, _ = extractor
    mensajes = [
        {"fecha": "01/10/25 12:00:00", "creador": "Ana", "mensaje": "Viejo"},
        {"fecha": "15/10/25 12:00:00", "creador": "Luis", "mensaje": "Nuevo"},
    ]

    filtrados = extractor_obj._filtrar_por_fecha(mensajes, "2025-10-10")

    assert len(filtrados) == 1
    assert filtrados[0]["creador"] == "Luis"


def test_agrupar_mensajes_consecutivos_crea_bloques(extractor):
    extractor_obj, _, _ = extractor
    mensajes = [
        {"fecha": "01/10/25 10:00:00", "creador": "Ana", "mensaje": "Receta"},
        {
            "fecha": "01/10/25 10:01:00",
            "creador": "Ana",
            "mensaje": "Ingredientes: 1 huevo",
        },
        {"fecha": "01/10/25 10:02:00", "creador": "Luis", "mensaje": "Hola"},
    ]

    bloques = extractor_obj._agrupar_mensajes_consecutivos(mensajes)

    assert len(bloques) == 1
    assert "Ingredientes" in bloques[0]["texto"]


def test_procesar_archivo_con_error_de_lectura(extractor):
    extractor_obj, _, _ = extractor

    with patch("builtins.open", side_effect=IOError("boom")):
        resultado = extractor_obj.procesar_archivo("test.txt")

    assert resultado["error"] == "boom"


def test_actualizar_estado_guarda_archivo(extractor):
    extractor_obj, _, supabase = extractor
    supabase.guardar_estado_procesamiento.return_value = True

    with (
        patch("os.makedirs") as makedirs,
        patch("builtins.open", mock_open()) as mocked_open,
    ):
        extractor_obj._actualizar_estado_procesamiento("01/10/25 10:00:00")

    makedirs.assert_called_once_with("state", exist_ok=True)
    assert mocked_open.called
