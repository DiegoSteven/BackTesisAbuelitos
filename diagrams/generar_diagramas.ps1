# Script para generar todas las imágenes PNG de los diagramas PlantUML
# Asegúrate de tener Java instalado: java -version

# Configuración
$diagramsPath = "$PSScriptRoot"
$plantUmlUrl = "https://github.com/plantuml/plantuml/releases/download/v1.2024.3/plantuml-1.2024.3.jar"
$plantUmlJar = "$diagramsPath\plantuml.jar"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Generador de Diagramas PlantUML" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Java
Write-Host "1. Verificando Java..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-String "version"
    Write-Host "   ✓ Java encontrado: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Java no encontrado. Por favor instala Java desde:" -ForegroundColor Red
    Write-Host "     https://www.java.com/download/" -ForegroundColor Red
    exit 1
}

# Descargar PlantUML si no existe
if (-Not (Test-Path $plantUmlJar)) {
    Write-Host ""
    Write-Host "2. Descargando PlantUML..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $plantUmlUrl -OutFile $plantUmlJar
        Write-Host "   ✓ PlantUML descargado exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ Error al descargar PlantUML" -ForegroundColor Red
        Write-Host "   Descárgalo manualmente desde: $plantUmlUrl" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "2. PlantUML encontrado" -ForegroundColor Green
}

# Crear carpeta de salida
$outputPath = "$diagramsPath\output"
if (-Not (Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath | Out-Null
    Write-Host "   ✓ Carpeta de salida creada: $outputPath" -ForegroundColor Green
}

# Generar diagramas
Write-Host ""
Write-Host "3. Generando diagramas..." -ForegroundColor Yellow
Write-Host ""

$pumlFiles = Get-ChildItem -Path $diagramsPath -Filter "*.puml"
$count = 0

foreach ($file in $pumlFiles) {
    $count++
    Write-Host "   [$count/$($pumlFiles.Count)] Generando: $($file.Name)" -ForegroundColor Cyan
    
    try {
        # Generar PNG
        java -jar $plantUmlJar -tpng -o "$outputPath" $file.FullName 2>&1 | Out-Null
        
        $pngFile = Join-Path $outputPath ($file.BaseName + ".png")
        if (Test-Path $pngFile) {
            $fileSize = (Get-Item $pngFile).Length / 1KB
            Write-Host "       ✓ Generado: $($file.BaseName).png ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "       ✗ Error al generar $($file.Name)" -ForegroundColor Red
        }
    } catch {
        Write-Host "       ✗ Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Proceso completado" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Los diagramas PNG se encuentran en:" -ForegroundColor Green
Write-Host "$outputPath" -ForegroundColor White
Write-Host ""
Write-Host "Total de diagramas generados: $count" -ForegroundColor Green
Write-Host ""

# Abrir carpeta de salida
$response = Read-Host "¿Deseas abrir la carpeta de salida? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    Start-Process $outputPath
}
