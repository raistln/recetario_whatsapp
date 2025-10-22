# 🍳 Recetario WhatsApp

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Mistral AI](https://img.shields.io/badge/mistral--ai-v1-green.svg)](https://mistral.ai/)
[![Supabase](https://img.shields.io/badge/supabase-2.0+-black.svg)](https://supabase.com/)

> Convierte chats de WhatsApp en un recetario interactivo usando IA. Extrae recetas automáticamente con Mistral AI y guárdalas en una base de datos con interfaz web moderna.

## ✨ Características

- 🧠 **Extracción automática** de recetas desde chats de WhatsApp usando Mistral AI
- 📦 **Bloques optimizados** para reducir llamadas API (80% más eficiente)
- 🗄️ **Base de datos Supabase** con interfaz web moderna
- 🔍 **Búsqueda y filtros** por ingredientes, autor, fecha
- 📱 **Interfaz responsive** con Streamlit
- 🚀 **Configuración automática** con un solo comando

## 🚀 Instalación Rápida

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/recetario-whatsapp.git
cd recetario-whatsapp

# 2. Configura el entorno automáticamente
python setup.py

# 3. Ejecuta la aplicación
python run_app.py
```

## 📋 ¿Qué hace?

1. **Procesa archivos de WhatsApp** y extrae mensajes automáticamente
2. **Usa IA para identificar recetas** con ingredientes y pasos
3. **Guarda en base de datos** con información estructurada
4. **Muestra en interfaz web** con búsqueda y filtros
5. **Optimiza tokens** para reducir costos de API

## 🛠️ Configuración

### Variables de Entorno

Crea un archivo `.env` con:

```env
# API de Mistral AI (obtener en https://console.mistral.ai/)
MISTRAL_API_KEY=sk-tu-api-key-aqui

# Base de datos Supabase (obtener en https://supabase.com/dashboard)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_STORAGE_BUCKET=recetas
```

### Requisitos

- **Python 3.11** (usa `py -3.11` en Windows)
- **Conexión a internet** para descargar dependencias
- **API keys** de Mistral y Supabase

## 📁 Estructura del Proyecto

```
recetario-whatsapp/
├─ 📄 setup.py              # Configuración automática
├─ 🚀 run_app.py            # Ejecutar aplicación
├─ 📱 app_streamlit.py      # Interfaz web principal
├─ ⚙️ pyproject.toml        # Dependencias (Poetry)
├─ 📚 README.md             # Esta documentación
├─ 🔒 .env                  # Variables de entorno
├─ 📁 src/                  # Código fuente
│  ├─ 📄 __init__.py
│  ├─ 🍳 recetario_whatsapp/
│  │  ├─ 📄 __init__.py
│  │  ├─ 🔍 extractor.py    # Procesa archivos WhatsApp
│  │  ├─ 🤖 mistral_client.py # Cliente IA Mistral
│  │  └─ 🗄️ supabase_utils.py # Manejo de base de datos
├─ 📁 samples/              # Archivos de ejemplo
├─ 📁 tests/                # Tests unitarios e integración
├─ 📁 docs/                 # Documentación técnica
├─ 📁 sql/                  # Scripts SQL
└─ 🔒 .gitignore           # Archivos a ignorar en Git
```

## 🔧 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `python setup.py` | Configura Python 3.11 + dependencias |
| `python run_app.py` | Inicia la aplicación web |
| `python -m pytest tests/` | Ejecuta todos los tests |
| `python -m src.recetario_whatsapp --file archivo.txt` | Procesa un archivo de WhatsApp |

## 🎯 Uso

### Procesar un Archivo de WhatsApp

```bash
# Procesa un archivo de chat exportado de WhatsApp
python -m src.recetario_whatsapp.extractor --file "tu_archivo.txt"
```

### Usar la Interfaz Web

```bash
# Inicia la aplicación web
python run_app.py

# Abre http://localhost:8501 en tu navegador
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar test específico
python -m pytest tests/test_extractor.py -v

# Test de flujo completo
python -m pytest tests/test_flujo_completo.py -v
```

## 📊 Optimización

### Rendimiento:
- ✅ **Bloques de 15K tokens** (vs 1K antes)
- ✅ **Múltiples recetas** por llamada API
- ✅ **Reducción 80%** en llamadas API
- ✅ **Mistral Small** (eficiente y económico)

### Costo:
- ✅ **80% más económico** que el procesamiento individual
- ✅ **Fallback automático** si la IA falla
- ✅ **Context window 32K** tokens

## 🐛 Problemas Comunes

| Error | Solución | Documentación |
|-------|----------|---------------|
| `ModuleNotFoundError: mistralai` | Actualizar API v0 → v1 | `docs/SOLUCION_MISTRALAI.md` |
| `Respuesta no válida de Mistral` | Prompt simplificado | `docs/SOLUCION_MISTRAL_ERROR.md` |
| `Mistral object has no attribute '_client'` | Context manager | `docs/SOLUCION_MISTRAL_API.md` |

## 📚 Documentación Técnica

Consulta la carpeta [`docs/`](docs/) para:
- ✅ Guías de solución de problemas
- ✅ Configuración paso a paso
- ✅ Optimizaciones implementadas
- ✅ Troubleshooting específico

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [`LICENSE`](LICENSE) para más detalles.

## 🙋‍♂️ Soporte

- 📖 **Documentación:** [`docs/`](docs/)
- 🐛 **Issues:** [GitHub Issues](https://github.com/tu-usuario/recetario-whatsapp/issues)
- 💬 **Discusiones:** [GitHub Discussions](https://github.com/tu-usuario/recetario-whatsapp/discussions)

---

**⭐ Si te gusta este proyecto, dale una estrella en GitHub!**

*Versión 0.1.0 - Optimizado y simplificado* ✨
