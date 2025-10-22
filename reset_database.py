#!/usr/bin/env python3
"""
Script para resetear la base de datos de Supabase.
Elimina todas las recetas para empezar limpio.
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def resetear_base_datos():
    """Elimina todas las recetas de la base de datos."""
    print("🗑️ Reseteando base de datos de Supabase...")
    print("=" * 50)

    try:
        from recetario_whatsapp.supabase_utils import SupabaseManager

        # Crear gestor de Supabase
        supabase_manager = SupabaseManager()

        # Obtener todas las recetas
        print("📊 Obteniendo recetas existentes...")
        recetas = supabase_manager.obtener_recetas()
        total_recetas = len(recetas)

        if total_recetas == 0:
            print("✅ La base de datos ya está vacía")
            return True

        print(f"🗑️ Eliminando {total_recetas} recetas...")

        # Eliminar todas las recetas una por una
        eliminadas = 0
        errores = 0

        for receta in recetas:
            if supabase_manager.eliminar_receta(receta['id']):
                eliminadas += 1
                if eliminadas % 10 == 0:  # Mostrar progreso cada 10
                    print(f"   Eliminadas: {eliminadas}/{total_recetas}")
            else:
                errores += 1
                print(f"   ❌ Error eliminando receta ID: {receta['id']}")

        print("
📊 Resultados del reseteo:"        print(f"   ✅ Recetas eliminadas: {eliminadas}")
        print(f"   ❌ Errores: {errores}")

        if errores == 0:
            print("🎉 ¡Base de datos reseteada completamente!")
            return True
        else:
            print("⚠️ Base de datos reseteada parcialmente")
            return False

    except Exception as e:
        print(f"❌ Error durante el reseteo: {e}")
        return False

def main():
    """Función principal."""
    print("🗑️ RESETADOR DE BASE DE DATOS - Recetario WhatsApp")
    print("=" * 60)

    # Ejecutar reseteo directo (sin confirmación para automatización)
    success = resetear_base_datos()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Base de datos reseteada exitosamente")
        print("   Ahora puedes empezar con pruebas limpias")
        print("   Ejecuta: python run_app.py")
    else:
        print("❌ Error durante el reseteo")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
