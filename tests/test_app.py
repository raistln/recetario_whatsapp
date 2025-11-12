"""Tests básicos para la capa Streamlit."""

from unittest.mock import MagicMock, patch

from src.recetario_whatsapp import app


@patch("app_streamlit.st")
def test_get_supabase_manager_success(mock_st, mock_env_vars):
    """Debe devolver la instancia creada cuando no hay errores."""

    gestor_mock = MagicMock()

    with patch(
        "app_streamlit.SupabaseManager", return_value=gestor_mock
    ) as manager_cls:
        resultado = app.get_supabase_manager()

    assert resultado is gestor_mock
    manager_cls.assert_called_once()
    mock_st.error.assert_not_called()


@patch("app_streamlit.st")
def test_get_extractor_success(mock_st, mock_env_vars):
    """Debe devolver instancia del extractor cuando no falla."""

    extractor_mock = MagicMock()

    with patch(
        "app_streamlit.WhatsAppExtractor", return_value=extractor_mock
    ) as extractor_cls:
        resultado = app.get_extractor()

    assert resultado is extractor_mock
    extractor_cls.assert_called_once()
    mock_st.error.assert_not_called()


@patch("app_streamlit.st")
def test_main_corta_ejecucion_si_no_hay_servicios(mock_st, mock_env_vars):
    """La función principal muestra un error y termina si no hay servicios."""

    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.error = MagicMock()

    with (
        patch("app_streamlit.get_supabase_manager", return_value=None),
        patch("app_streamlit.get_extractor", return_value=None),
    ):
        app.main()

    mock_st.error.assert_called_once_with(
        "No se pudieron inicializar los servicios necesarios. Verifica la configuración."
    )
