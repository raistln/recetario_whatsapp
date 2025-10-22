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
