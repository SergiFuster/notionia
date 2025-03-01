# Script para ejecutar tanto el backend como el frontend

# Iniciar el backend en una nueva ventana de PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\backend; pip install -e .; cd src; python main.py"

# Esperar un momento para que el backend se inicie
Start-Sleep -Seconds 3

# Iniciar el frontend en una nueva ventana de PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\frontend; npm install; npm start"

Write-Host "Aplicación iniciada. El backend está corriendo en http://localhost:8000 y el frontend en http://localhost:3000"
