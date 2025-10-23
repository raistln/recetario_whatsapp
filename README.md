# 🍳 Recetario WhatsApp

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Storage-3FCF8E.svg)](https://supabase.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Gallery-blue.svg)](https://cloudinary.com/)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency_Management-60A5FA.svg)](https://python-poetry.org/)

> Convierte chats de WhatsApp en un recetario colaborativo con IA, galería de fotos Cloudinary y administración web en tiempo real.

## ✨ Highlights

- 🧠 **Extracción con IA (Mistral)** de ingredientes y pasos.
- 📚 **Base de datos Supabase** con migraciones SQL versionadas.
- 🖼️ **Galería multifoto** por receta integrada con Cloudinary (autor por imagen).
- 🔎 **Búsqueda en vivo, filtros por autor, estado de fotos y fecha.**
- ⚙️ **Deploy rápido con Streamlit** + modo desarrollador para ejecuciones locales.
- 🧪 **Pipeline de pruebas y scripts de mantenimiento** listos.

## 🚀 Instalación (Poetry)

```bash
# Clona el repositorio
git clone https://github.com/[tu-usuario-github]/recetario-whatsapp.git
cd recetario-whatsapp

# Crea el entorno virtual con Poetry
poetry install

# Activa el shell
poetry shell

# Ejecuta el panel Streamlit
poetry run streamlit run app_streamlit.py
```

> 💡 Alternativa con `pip`: consulta `docs/INSTALL.md` si prefieres entorno manual.

## 🔐 Variables de entorno (`.env`)

```env
# IA
MISTRAL_API_KEY=sk-tu-api-key

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJhbGciOi... (anon/public)
SUPABASE_STORAGE_BUCKET=recetas

# Cloudinary
CLOUDINARY_URL=cloudinary://<api_key>:<secret>@<cloud_name>
```

## 🧭 Flujo Principal

1. **Carga un `.txt` exportado** de WhatsApp (modo panel o CLI).
2. El extractor agrupa recetas, autor y metadatos.
3. **Mistral IA** limpia ingredientes y pasos (tokens optimizados).
4. Se guardan en **Supabase** (tabla `recetas`) + galería (JSONB `imagenes`).
5. **Streamlit** muestra fichas con edición, filtros y carruseles.

## 🖼️ Galería Cloudinary

- Botón “📸 Subir Foto” acepta múltiples archivos.
- Cada imagen pide autor, sube a Cloudinary y guarda URL + metadatos.
- Carrusel elegante con selectbox y contador.
- Botón “🗑️ Eliminar imagen” actualiza Supabase + limpia `url_imagen` legacy.

## 🍽️ Panel Streamlit

- Búsqueda instantánea por nombre, ingredientes o autor.
- Expander por receta con ingredientes, pasos y fotos.
- Sección “⚙️ Configuración” para activar/desactivar módulo de imágenes.
- Estadísticas generales (total recetas, creadores, fotos).
- Formularios para crear/editar/eliminar recetas manualmente.

### Modo desarrollador

```bash
# Ejecuta con recarga en caliente
poetry run streamlit run app_streamlit.py --server.runOnSave true

# Modo ancho completo
STREAMLIT_SERVER_HEADLESS=true poetry run streamlit run app_streamlit.py
```

## 🧰 Comandos útiles

| Acción | Comando |
|--------|---------|
| Ejecutar extractor CLI | `poetry run python -m src.recetario_whatsapp.extractor --file salida.txt` |
| Tests rápidos | `poetry run pytest` |
| Lint (ruff) | `poetry run ruff check .` |
| Formateo (ruff) | `poetry run ruff format .` |

## 🗃️ Estructura Clave

```
recetario-whatsapp/
├─ app_streamlit.py        # Panel principal (galería, filtros, CRUD)
├─ src/recetario_whatsapp/
│  ├─ extractor.py         # Limpieza de chats y batching IA
│  ├─ mistral_client.py    # Cliente Mistral (v1)
│  ├─ supabase_utils.py    # SDK Supabase + almacenamiento Cloudinary
├─ sql/
│  ├─ migration_add_images.sql
│  └─ rollback_migration.sql
├─ docs/
│  ├─ INSTALL.md
│  └─ TROUBLESHOOTING.md
├─ tests/
│  └─ test_extractor.py
└─ README.md
```

## 📸 Migraciones & Galería

- `sql/migration_add_images.sql`: añade columna `imagenes` (JSONB) manteniendo `url_imagen` legacy.
- `sql/rollback_migration.sql`: reversión segura (quita galería si fuese necesario).
- El panel detecta recetas antiguas y convierte su `url_imagen` en la primera entrada del carrusel.

## 🔄 CLI de extracción

```bash
poetry run python -m src.recetario_whatsapp.extractor \
  --file samples/chat.txt \
  --output outputs/recetas.json
```

- Admite parámetros de batching (`--batch-size`) y modo debug (`--debug`).
- Los resultados se insertan desde `app_streamlit.py` o mediante scripts personalizados.

## 🧪 Pruebas & QA

- Tests unitarios con PyTest (`tests/`).
- Scripts de verificación manual en `samples/`.
- Se recomienda ejecutar `poetry run pytest -q` tras cambios en el extractor.

## 🤝 Contribución

- **Fork**, rama (`feature/nueva-feature`), PR con descripción clara.
- Usa `poetry run ruff check` y `poetry run pytest` antes de subir.
- Documenta cambios relevantes en el README o `docs/`.

## 👨‍💻 Autor & Contacto

**Nombre:** [Tu Nombre Aquí]  
**Email:** [tu.email@ejemplo.com]  
**GitHub:** [@tu-usuario-github](https://github.com/tu-usuario-github)  
**LinkedIn:** [Tu Perfil LinkedIn](https://linkedin.com/in/tu-perfil)  
**WhatsApp Grupo:** [Enlace al grupo si aplica]

> 💬 Para soporte o colaboraciones, envía un email o abre un issue en GitHub.

## 📄 Licencia & Créditos

- MIT License (ver `LICENSE`).
- Stack: Python 3.11, Streamlit, Mistral, Supabase, Cloudinary, Poetry.
- UI inspirada en el catálogo original del grupo de WhatsApp 🧡

---

**¿Te resultó útil?** ¡Dale ⭐️ en GitHub y comparte tus recetas!
