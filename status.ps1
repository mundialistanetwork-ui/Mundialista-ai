Write-Host "=== MUNDIALISTA AI STATUS ===" -ForegroundColor Cyan
Write-Host "Location: C:\Users\bayen\mundialista-ai"
Write-Host "Files: 45 Python files"
Write-Host "Venv: " -ForegroundColor Green
python -c "from prediction_engine import predict; print('Engine: OK')"
python -c "from chart_generator import generate_all_charts; print('Charts: OK')"
Write-Host "=== READY ===" -ForegroundColor Green
