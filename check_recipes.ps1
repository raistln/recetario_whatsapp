# Script para verificar las recetas guardadas usando Poetry
Write-Host "Verificando recetas guardadas..." -ForegroundColor Green

# Ejecutar el verificador de recetas
poetry run python -c "
import sys
sys.path.insert(0, 'src')
from dotenv import load_dotenv
load_dotenv()
from recetario_whatsapp.supabase_utils import SupabaseManager
sm = SupabaseManager()
recetas = sm.obtener_recetas()
print(f'Total recetas: {len(recetas)}')
if recetas:
    for i, r in enumerate(recetas, 1):
        print(f'{i}. {r[\"nombre_receta\"]} por {r[\"creador\"]}')
        print(f'   🥘 {r[\"ingredientes\"]}')
        print(f'   👨‍🍳 {r.get(\"pasos_preparacion\", \"Sin pasos\")}')
        print()
else:
    print('No hay recetas guardadas')
"

Write-Host "`nPresiona Enter para continuar..." -ForegroundColor Yellow
Read-Host
