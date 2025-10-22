# 🔧 Solución: Poetry no encuentra Python 3.11

## 🚨 Problema
Tienes Python 3.11 instalado pero Poetry no lo encuentra y dice "se requiere python 3.11".

## 🎯 Solución Rápida

### Paso 1: Diagnóstico
```bash
python diagnose_python.py
```
Este script te dirá exactamente qué está pasando y dónde está tu Python 3.11.

### Paso 2: Solución Automática
```bash
python quick_fix_windows.py
```
Este script:
- ✅ Busca Python 3.11 en tu sistema
- ✅ Configura Poetry para usarlo
- ✅ Instala todas las dependencias
- ✅ Prueba que todo funciona

### Paso 3: Verificación
```bash
python verify_setup.py
```

## 🔍 Si la Solución Rápida No Funciona

### Opción A: Configuración Manual
```bash
# 1. Encontrar Python 3.11
py -3.11 -c "import sys; print(sys.executable)"

# 2. Usar esa ruta con Poetry
poetry env use "RUTA_QUE_TE_DIO_EL_COMANDO_ANTERIOR"

# 3. Instalar dependencias
poetry install --with dev
```

### Opción B: Reinstalar Python 3.11
1. Descargar Python 3.11.8 desde: https://www.python.org/downloads/release/python-3118/
2. **IMPORTANTE**: Marcar "Add Python to PATH" durante la instalación
3. Reiniciar la terminal
4. Ejecutar: `python quick_fix_windows.py`

### Opción C: Usar Python Launcher
```bash
# Si tienes py launcher instalado
poetry env use py -3.11
poetry install --with dev
```

## 🐛 Problemas Comunes y Soluciones

### Error: "Python 3.11 not found"
**Solución:**
```bash
# Verificar que Python 3.11 está instalado
py -3.11 --version

# Si no funciona, reinstalar Python 3.11 con "Add to PATH"
```

### Error: "Poetry command not found"
**Solución:**
```bash
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python -

# O con pip
pip install poetry
```

### Error: "Permission denied"
**Solución:**
```bash
# Ejecutar como administrador o usar:
poetry install --no-dev
```

### Error: "Virtual environment not found"
**Solución:**
```bash
# Limpiar y recrear
poetry env remove --all
poetry env use "RUTA_DE_PYTHON_3.11"
poetry install
```

## 📋 Scripts de Ayuda Disponibles

| Script | Propósito |
|--------|-----------|
| `diagnose_python.py` | Diagnostica problemas con Python 3.11 |
| `quick_fix_windows.py` | Solución rápida para Windows |
| `fix_python_detection.py` | Solución completa con detección |
| `clean_and_setup.py` | Configuración completa del proyecto |
| `verify_setup.py` | Verifica que todo está bien |

## 🎯 Comandos de Verificación

```bash
# Verificar Python
python --version

# Verificar Poetry
poetry --version

# Verificar entorno de Poetry
poetry env info

# Verificar dependencias
poetry run python -c "import streamlit; print('OK')"
```

## 🆘 Si Nada Funciona

1. **Ejecutar diagnóstico completo:**
   ```bash
   python diagnose_python.py
   ```

2. **Compartir el resultado** del diagnóstico para ayuda específica

3. **Reinstalar todo desde cero:**
   ```bash
   # Desinstalar Poetry
   pip uninstall poetry
   
   # Reinstalar Poetry
   curl -sSL https://install.python-poetry.org | python -
   
   # Ejecutar solución rápida
   python quick_fix_windows.py
   ```

## ✅ Verificación Final

Cuando todo esté funcionando, deberías poder ejecutar:
```bash
poetry run python run_app.py
```

Y ver la aplicación Streamlit funcionando correctamente.

---

**💡 Tip:** Si sigues teniendo problemas, ejecuta `python diagnose_python.py` y comparte el resultado para obtener ayuda específica.
