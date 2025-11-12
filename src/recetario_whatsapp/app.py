"""Compatibilidad de import para pruebas de la app Streamlit."""

from app_streamlit import get_supabase_manager, get_extractor, main

__all__ = ["get_supabase_manager", "get_extractor", "main"]
