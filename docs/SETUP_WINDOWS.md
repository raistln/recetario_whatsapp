# 🪟 Configuración en Windows

Guía específica para configurar el Recetario WhatsApp en Windows con Python 3.11.

## 📋 Requisitos Previos

### 1. Python 3.11
- Descarga Python 3.11 desde: https://www.python.org/downloads/release/python-3118/
- **IMPORTANTE**: Selecciona "Add Python to PATH" durante la instalación
- Verifica la instalación:
  ```cmd
  python --version
  # Debe mostrar: Python 3.11.x
  ```

### 2. Poetry
```cmd
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python -

# O usando pip
pip install poetry
```

## 🚀 Configuración Automática

### Opción 1: Script Automático (Recomendado)
```cmd
# Ejecutar configuración automática
python clean_and_setup.py

# Verificar configuración
python verify_setup.py
```

### Opción 2: Configuración Manual

#### 1. Limpiar entorno anterior
```cmd
# Eliminar directorios de cache
rmdir /s /q .venv
rmdir /s /q venv
rmdir /s /q __pycache__
rmdir /s /q .pytest_cache
rmdir /s /q htmlcov

# Eliminar archivos
del poetry.lock
del .coverage
```

#### 2. Configurar Poetry
```cmd
# Configurar Poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true
poetry env remove --all
```

#### 3. Instalar dependencias
```cmd
# Instalar dependencias principales
poetry install

# Instalar dependencias de desarrollo
poetry install --with dev
```

#### 4. Configurar variables de entorno
```cmd
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

## 🔧 Solución de Problemas Comunes

### Error: "Python not found"
```cmd
# Verificar que Python está en PATH
where python

# Si no está, agregar manualmente al PATH:
# 1. Buscar "Variables de entorno" en el menú inicio
# 2. Editar variables de entorno del sistema
# 3. Agregar la ruta de Python 3.11 al PATH
```

### Error: "Poetry not found"
```cmd
# Reinstalar Poetry
curl -sSL https://install.python-poetry.org | python -

# O usar pip
pip install --user poetry

# Agregar Poetry al PATH si es necesario
# La ruta suele ser: %APPDATA%\Python\Scripts
```

### Error: "Permission denied"
```cmd
# Ejecutar como administrador o usar:
poetry install --no-dev
```

### Error: "Virtual environment not found"
```cmd
# Recrear entorno virtual
poetry env remove --all
poetry install
```

## 🧪 Verificación

```cmd
# Verificar configuración
python verify_setup.py

# Ejecutar tests
poetry run python run_tests.py

# Ejecutar aplicación
poetry run python run_app.py
```

## 📁 Estructura Esperada

```
recetario-whatsapp/
├── .venv/                 # Entorno virtual (creado por Poetry)
├── .env                   # Variables de entorno (crear desde .env.example)
├── src/recetario_whatsapp/ # Código fuente
├── tests/                 # Tests
├── samples/               # Archivos de ejemplo
├── sql/                   # Scripts SQL
├── clean_and_setup.py    # Script de configuración
├── verify_setup.py       # Script de verificación
└── run_app.py            # Script para ejecutar la app
```

## 🎯 Comandos Útiles

```cmd
# Activar entorno virtual manualmente
.venv\Scripts\activate

# Desactivar entorno virtual
deactivate

# Ver información del entorno
poetry env info

# Ver dependencias instaladas
poetry show

# Actualizar dependencias
poetry update

# Ejecutar aplicación
poetry run python run_app.py

# Ejecutar tests
poetry run python run_tests.py

# Verificar configuración
python verify_setup.py
```

## 🆘 Si Algo Sale Mal

1. **Ejecutar limpieza completa:**
   ```cmd
   python clean_and_setup.py
   ```

2. **Verificar configuración:**
   ```cmd
   python verify_setup.py
   ```

3. **Reinstalar Poetry:**
   ```cmd
   pip uninstall poetry
   curl -sSL https://install.python-poetry.org | python -
   ```

4. **Reinstalar Python 3.11:**
   - Desinstalar versiones anteriores
   - Descargar e instalar Python 3.11.8
   - Asegurar que esté en PATH

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `python verify_setup.py` y comparte el resultado
2. Verifica que Python 3.11 esté instalado correctamente
3. Asegúrate de que Poetry esté en el PATH
4. Revisa que no haya conflictos con versiones anteriores de Python
