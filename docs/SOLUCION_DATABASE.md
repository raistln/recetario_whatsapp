# 🗄️ Solución: Error de Tabla No Encontrada

## 🚨 Problema
```
Error obteniendo creadores: Could not find the table 'public.recetas' in the schema cache
Error obteniendo recetas: Could not find the table 'public.recetas' in the schema cache
```

## ✅ Solución Rápida

### Opción 1: Script Automático (Recomendado)
```bash
python setup_database.py
```

### Opción 2: Crear Tabla Manualmente

#### Paso 1: Ir a Supabase Dashboard
1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Ve a **"SQL Editor"** en el menú lateral

#### Paso 2: Ejecutar SQL
Copia y pega este código en el SQL Editor:

```sql
-- Crear tabla de recetas
CREATE TABLE IF NOT EXISTS recetas (
  id SERIAL PRIMARY KEY,
  creador TEXT NOT NULL,
  nombre_receta TEXT,
  ingredientes TEXT NOT NULL,
  pasos_preparacion TEXT,
  tiene_foto BOOLEAN DEFAULT FALSE,
  url_imagen TEXT,
  fecha_mensaje TIMESTAMP WITH TIME ZONE
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_recetas_creador ON recetas(creador);
CREATE INDEX IF NOT EXISTS idx_recetas_fecha ON recetas(fecha_mensaje);
CREATE INDEX IF NOT EXISTS idx_recetas_nombre ON recetas(nombre_receta);
```

#### Paso 3: Ejecutar
1. Haz clic en **"Run"** para ejecutar el SQL
2. Verifica que aparezca "Success" en la consola

### Opción 3: Usar Archivo SQL
```bash
# El archivo create_table_recetas.sql ya está listo
# Copia su contenido y pégalo en Supabase SQL Editor
```

## 🔍 Verificación

Después de crear la tabla, verifica que todo funciona:

```bash
# Verificar base de datos
python check_database.py

# O verificar con la aplicación
python start_app.py
```

## 📋 Estructura de la Tabla

La tabla `recetas` tiene las siguientes columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | SERIAL PRIMARY KEY | ID único de la receta |
| `creador` | TEXT NOT NULL | Nombre del creador |
| `nombre_receta` | TEXT | Nombre de la receta |
| `ingredientes` | TEXT NOT NULL | Lista de ingredientes |
| `pasos_preparacion` | TEXT | Pasos de preparación |
| `tiene_foto` | BOOLEAN | Si tiene foto (default: false) |
| `url_imagen` | TEXT | URL de la imagen |
| `fecha_mensaje` | TIMESTAMP | Fecha del mensaje original |

## 🧪 Datos de Ejemplo

El script `setup_database.py` también crea datos de ejemplo:

- **Tarta de Queso** (Ana)
- **Gazpacho** (Luis) 
- **Pasta Carbonara** (Marta)

## 🔧 Scripts Disponibles

| Script | Propósito |
|--------|-----------|
| `setup_database.py` | Configuración automática completa |
| `check_database.py` | Verificar estado de la base de datos |
| `create_table_recetas.sql` | SQL para crear la tabla |

## 🆘 Si Sigue Fallando

### 1. Verificar Variables de Entorno
```bash
# Verificar que .env esté configurado
cat .env
```

### 2. Verificar Conexión
```bash
python check_database.py
```

### 3. Verificar Permisos
- Asegúrate de que tu API key tenga permisos de lectura/escritura
- Verifica que el proyecto de Supabase esté activo

### 4. Recrear Tabla
```sql
-- Si la tabla existe pero tiene problemas
DROP TABLE IF EXISTS recetas;
-- Luego ejecutar el CREATE TABLE de nuevo
```

## ✅ Verificación Final

Cuando todo esté funcionando, deberías poder:

1. **Ejecutar la aplicación:**
   ```bash
   python start_app.py
   ```

2. **Ver recetas en la interfaz** (si creaste datos de ejemplo)

3. **Procesar archivos de WhatsApp** sin errores

---

**💡 Una vez creada la tabla, la aplicación funcionará perfectamente!**
