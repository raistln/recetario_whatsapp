-- Script de migración segura para añadir galería de imágenes
-- Ejecuta en Supabase SQL Editor sin perder datos existentes
-- Compatible con tabla estado_procesamiento y funciones actuales

-- Paso 1: Añadir nueva columna imagenes con valor por defecto
-- Esto no afecta datos existentes ni la tabla estado_procesamiento
ALTER TABLE recetas ADD COLUMN IF NOT EXISTS imagenes JSONB DEFAULT '[]'::jsonb;

-- Paso 2: Migrar datos existentes (opcional)
-- Si tienes recetas con url_imagen, convértelas a formato imagenes
-- Preserva compatibilidad con código actual
UPDATE recetas
SET imagenes =
  CASE
    WHEN url_imagen IS NOT NULL AND url_imagen != '' THEN
      jsonb_build_array(jsonb_build_object('url', url_imagen, 'autor', creador))
    ELSE '[]'::jsonb
  END
WHERE imagenes = '[]'::jsonb OR imagenes IS NULL;

-- Paso 3: Verificar migración (opcional)
-- Ejecuta para ver cuántas recetas se migraron
-- SELECT id, creador, url_imagen, imagenes FROM recetas WHERE url_imagen IS NOT NULL LIMIT 5;

-- Crear índices para mejor rendimiento (si no existen)
-- No afecta estado_procesamiento ni otras funciones
CREATE INDEX IF NOT EXISTS idx_recetas_creador ON recetas(creador);
CREATE INDEX IF NOT EXISTS idx_recetas_fecha ON recetas(fecha_mensaje);
CREATE INDEX IF NOT EXISTS idx_recetas_nombre ON recetas(nombre_receta);

-- Paso 4: Verificación final
-- Cuenta recetas totales, con imágenes y con url_imagen
-- SELECT
--   COUNT(*) as total_recetas,
--   COUNT(*) FILTER (WHERE imagenes != '[]'::jsonb) as con_imagenes,
--   COUNT(*) FILTER (WHERE url_imagen IS NOT NULL) as con_url_imagen
-- FROM recetas;

-- ¡Listo! Tu tabla recetas ahora soporta galería de imágenes
-- - Los datos existentes se preservan
-- - estado_procesamiento sigue funcionando igual
-- - El código Python detecta automáticamente recetas antiguas vs nuevas
