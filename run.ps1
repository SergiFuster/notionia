# Iniciar el backend en una nueva ventana de PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\backend\src; fastapi dev"

# Esperar un momento para que el backend se inicie
Start-Sleep -Seconds 3

# Iniciar el frontend en una nueva ventana de PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\frontend; npm start"

Write-Host "Aplicaci n iniciada. El backend est  corriendo en http://localhost:8000 y el frontend en http://localhost:3000"
