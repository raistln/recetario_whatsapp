-- Script de rollback si algo sale mal (opcional)
-- Deshacer cambios sin perder datos

-- Quitar columna imagenes (si es necesario)
-- ALTER TABLE recetas DROP COLUMN IF EXISTS imagenes;

-- Restaurar datos desde url_imagen (si revertiste)
-- UPDATE recetas SET imagenes = '[]'::jsonb WHERE imagenes IS NULL;
