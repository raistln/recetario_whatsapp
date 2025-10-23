# 🧪 Tests del Recetario WhatsApp

Este directorio contiene todos los tests para asegurar la calidad y cobertura del código.

## 📊 Cobertura de Tests

Los tests están configurados para mantener una cobertura **superior al 90%** en todo el código.

## 🏗️ Estructura de Tests

```
tests/
├── conftest.py              # Configuración global y fixtures
├── test_mistral_client.py   # Tests para el cliente de Mistral
├── test_supabase_utils.py   # Tests para utilidades de Supabase
├── test_extractor.py        # Tests para el extractor de WhatsApp
├── test_app.py             # Tests para la aplicación Streamlit
├── test_integration.py     # Tests de integración
└── README.md               # Esta documentación
```

## 🚀 Ejecutar Tests

### Instalar dependencias de testing
```bash
poetry install --with dev
```

### Ejecutar todos los tests
```bash
poetry run python run_tests.py
```

### Ejecutar tests específicos
```bash
# Tests de un módulo específico
poetry run pytest tests/test_mistral_client.py -v

# Tests con cobertura detallada
poetry run pytest --cov=src/recetario_whatsapp --cov-report=html

# Tests de integración
poetry run pytest tests/test_integration.py -v
```

### Ver reporte de cobertura
```bash
# Abrir reporte HTML
open htmlcov/index.html
```

## 🧩 Tipos de Tests

### 1. **Tests Unitarios**
- `test_mistral_client.py`: Cliente de Mistral API
- `test_supabase_utils.py`: Operaciones con Supabase
- `test_extractor.py`: Procesamiento de archivos WhatsApp
- `test_app.py`: Funcionalidades de Streamlit

### 2. **Tests de Integración**
- `test_integration.py`: Flujos completos del sistema
- Casos edge y manejo de errores
- Procesamiento incremental
- Múltiples recetas en conversación

## 🔧 Configuración

### Variables de Entorno de Testing
El archivo `.env.test` contiene las variables necesarias para los tests:
```env
MISTRAL_API_KEY=test_mistral_key
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_supabase_key
SUPABASE_STORAGE_BUCKET=test-recetas
```

### Fixtures Disponibles
- `mock_env_vars`: Variables de entorno de prueba
- `mock_mistral_response`: Respuesta mock de Mistral
- `sample_whatsapp_text`: Texto de ejemplo de WhatsApp
- `sample_receta_data`: Datos de receta de ejemplo
- `mock_supabase_client`: Cliente mock de Supabase

## 📈 Métricas de Cobertura

Los tests cubren:
- ✅ **Inicialización** de clientes y servicios
- ✅ **Parsing** de mensajes de WhatsApp
- ✅ **Detección** de candidatos a recetas
- ✅ **Extracción** con IA (Mistral)
- ✅ **Operaciones CRUD** con Supabase
- ✅ **Interfaz** de Streamlit
- ✅ **Manejo de errores** en todos los niveles
- ✅ **Casos edge** y escenarios complejos

## 🐛 Debugging Tests

### Ejecutar con output detallado
```bash
poetry run pytest -v -s --tb=long
```

### Ejecutar un test específico
```bash
poetry run pytest tests/test_mistral_client.py::TestMistralClient::test_extraer_receta_success -v
```

### Ejecutar con coverage en tiempo real
```bash
poetry run pytest --cov=src/recetario_whatsapp --cov-report=term-missing --cov-report=html
```

## 📝 Escribir Nuevos Tests

1. **Seguir la convención de nombres**: `test_*.py`
2. **Usar fixtures** cuando sea posible
3. **Mockear dependencias externas** (APIs, bases de datos)
4. **Probar casos edge** y manejo de errores
5. **Mantener cobertura > 90%**

### Ejemplo de test
```python
def test_nueva_funcionalidad(self, mock_env_vars):
    """Test de nueva funcionalidad."""
    # Arrange
    expected_result = "resultado esperado"
    
    # Act
    actual_result = funcion_a_probar()
    
    # Assert
    assert actual_result == expected_result
```

## 🎯 Objetivos de Calidad

- **Cobertura**: > 90%
- **Tests unitarios**: Para cada función/método
- **Tests de integración**: Para flujos completos
- **Manejo de errores**: Todos los casos de error cubiertos
- **Casos edge**: Escenarios límite probados

