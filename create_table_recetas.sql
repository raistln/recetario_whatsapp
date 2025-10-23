-- Script SQL para crear la tabla de recetas en Supabase
-- Copia y pega este código en el SQL Editor de Supabase

-- Crear tabla de recetas
CREATE TABLE IF NOT EXISTS recetas (
  id SERIAL PRIMARY KEY,
  creador TEXT NOT NULL,
  nombre_receta TEXT,
  ingredientes TEXT NOT NULL,
  pasos_preparacion TEXT,
  tiene_foto BOOLEAN DEFAULT FALSE,
  url_imagen TEXT,
  imagenes JSONB DEFAULT '[]'::jsonb,
  fecha_mensaje TIMESTAMP WITH TIME ZONE
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_recetas_creador ON recetas(creador);
CREATE INDEX IF NOT EXISTS idx_recetas_fecha ON recetas(fecha_mensaje);
CREATE INDEX IF NOT EXISTS idx_recetas_nombre ON recetas(nombre_receta);

-- Opcional: Habilitar RLS (Row Level Security)
-- Descomenta las siguientes líneas si quieres habilitar seguridad a nivel de fila
-- ALTER TABLE recetas ENABLE ROW LEVEL SECURITY;

-- Opcional: Crear política para permitir todas las operaciones
-- Descomenta la siguiente línea si habilitaste RLS
-- CREATE POLICY "Allow all operations" ON recetas FOR ALL USING (true);

-- Insertar datos de ejemplo (opcional)
INSERT INTO recetas (creador, nombre_receta, ingredientes, pasos_preparacion, tiene_foto, imagenes, fecha_mensaje) VALUES
('Ana', 'Tarta de Queso', 
'- 200g galletas
- 100g mantequilla
- 500g queso crema
- 3 huevos
- 150g azúcar', 
'1. Triturar las galletas y mezclar con mantequilla
2. Forrar el molde con la mezcla
3. Batir el queso con azúcar y huevos
4. Verter sobre la base y hornear 30 min', 
false, '[]', '2025-01-21T10:00:00Z'),

('Luis', 'Gazpacho', 
'- 1kg tomates
- 1 pepino
- 1 pimiento verde
- 1 diente de ajo
- Aceite de oliva', 
'1. Triturar todos los ingredientes
2. Colar y refrigerar
3. Servir frío', 
 true, '[{"url": "https://ejemplo.com/gazpacho.jpg", "autor": "Luis"}]', '2025-01-21T11:30:00Z'),

('Marta', 'Pasta Carbonara', 
'- 400g pasta
- 200g panceta
- 4 huevos
- 100g queso parmesano
- Pimienta negra', 
'1. Cocinar la pasta según instrucciones
2. Freír la panceta hasta que esté crujiente
3. Batir los huevos con el queso
4. Mezclar todo con la pasta caliente', 
false, '[]', '2025-01-21T12:15:00Z');

