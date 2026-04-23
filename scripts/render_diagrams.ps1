param(
    [string]$JavaExe = "C:\Program Files\Eclipse Adoptium\jre-21.0.10.7-hotspot\bin\java.exe",
    [string]$PlantUmlJarPath = ".tools\plantuml.jar"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$diagramDir = Join-Path $repoRoot "assets\architecture\diagrams"
$classDiagram = Join-Path $diagramDir "class_diagram.wsd"
$runFlowDiagram = Join-Path $diagramDir "run_flow.wsd"
$classPng = Join-Path $diagramDir "class_diagram.png"
$runFlowPng = Join-Path $diagramDir "run_flow.png"
$tmpClassPng = Join-Path $diagramDir "Image-Sorter.png"
$tmpRunFlowPng = Join-Path $diagramDir "Image-Sorter-Run-Flow.png"
$jarFullPath = Join-Path $repoRoot $PlantUmlJarPath

if (-not (Test-Path $JavaExe)) {
    throw "Java executable not found at: $JavaExe"
}

if (-not (Test-Path $jarFullPath)) {
    Write-Host "PlantUML jar not found at $jarFullPath. Downloading latest jar..."
    $jarDir = Split-Path -Parent $jarFullPath
    if (-not (Test-Path $jarDir)) {
        New-Item -ItemType Directory -Path $jarDir | Out-Null
    }
    Invoke-WebRequest -Uri "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar" -OutFile $jarFullPath
}

if (-not (Test-Path $classDiagram)) {
    throw "Missing diagram file: $classDiagram"
}

if (-not (Test-Path $runFlowDiagram)) {
    throw "Missing diagram file: $runFlowDiagram"
}

Write-Host "Rendering class_diagram.wsd..."
& $JavaExe -jar $jarFullPath -tpng $classDiagram

if (Test-Path $tmpClassPng) {
    Move-Item $tmpClassPng $classPng -Force
}

Write-Host "Rendering run_flow.wsd..."
& $JavaExe -jar $jarFullPath -tpng $runFlowDiagram

if (Test-Path $tmpRunFlowPng) {
    Move-Item $tmpRunFlowPng $runFlowPng -Force
}

Write-Host "Done."
Write-Host "Generated:"
Write-Host " - $classPng"
Write-Host " - $runFlowPng"
