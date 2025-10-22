# Script para ejecutar el extractor usando Poetry
Write-Host "Ejecutando extractor con Poetry..." -ForegroundColor Green

# Ejecutar el extractor
poetry run python -m src.recetario_whatsapp.extractor --file "samples/Chat de WhatsApp con HungaRICOs 🤤🥒🍣🍤🥘.txt"

Write-Host "`nPresiona Enter para continuar..." -ForegroundColor Yellow
Read-Host
