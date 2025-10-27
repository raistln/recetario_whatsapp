#!/usr/bin/env python3
"""
Script para probar pandas y openpyxl en el entorno de Poetry
"""

def main():
    print("🔍 Probando pandas y openpyxl en Poetry...")

    try:
        import pandas as pd
        print('✅ Pandas importado correctamente')
        print('Versión de pandas:', pd.__version__)

        # Verificar si openpyxl está disponible
        try:
            import openpyxl
            print('✅ OpenPyXL importado correctamente')
            print('Versión de openpyxl:', openpyxl.__version__)
        except ImportError as e:
            print('❌ OpenPyXL no disponible:', e)

        # Probar carga de Excel
        try:
            # Crear un DataFrame de prueba
            df_test = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df_test.to_excel('test.xlsx', index=False)
            df_read = pd.read_excel('test.xlsx')
            print('✅ Pandas puede leer/escribir Excel correctamente')
            print('Shape del DataFrame:', df_read.shape)

            # Limpiar archivo de prueba
            import os
            os.remove('test.xlsx')

        except ImportError as e:
            print('❌ Error con Excel en pandas:', e)
        except Exception as e:
            print('⚠️ Error inesperado:', e)

    except ImportError as e:
        print('❌ Error importando pandas:', e)

    # Probar con el archivo Excel real del usuario
    print("\n📊 Probando con 'Recetas húngaras.xlsx'...")
    try:
        from src.recetario_whatsapp.extractor import WhatsAppExtractor

        if os.path.exists('Recetas húngaras.xlsx'):
            print('✅ Archivo encontrado')
            extractor = WhatsAppExtractor()
            resultado = extractor.procesar_archivo('Recetas húngaras.xlsx')
            print('📋 Resultado:')
            for key, value in resultado.items():
                print(f'  {key}: {value}')
        else:
            print('❌ Archivo Recetas húngaras.xlsx no encontrado')

    except Exception as e:
        print('❌ Error en el extractor:', e)

if __name__ == "__main__":
    import os
    main()
