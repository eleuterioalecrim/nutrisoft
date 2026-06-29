$ErrorActionPreference = "Stop"

$BaseDir = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $BaseDir

function Write-Section($Text) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Test-CommandExists($Command) {
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    return $null -ne $cmd
}

function Get-PythonCommand {
    if (Test-CommandExists "py") {
        try {
            & py -3.12 --version *> $null
            if ($LASTEXITCODE -eq 0) { return "py -3.12" }
        } catch {}

        try {
            & py -3 --version *> $null
            if ($LASTEXITCODE -eq 0) { return "py -3" }
        } catch {}
    }

    if (Test-CommandExists "python") {
        try {
            & python --version *> $null
            if ($LASTEXITCODE -eq 0) { return "python" }
        } catch {}
    }

    return $null
}

function Invoke-Python($PythonCommand, $Arguments) {
    if ($PythonCommand.StartsWith("py ")) {
        $parts = $PythonCommand.Split(" ")
        & $parts[0] $parts[1] @Arguments
    } else {
        & $PythonCommand @Arguments
    }
}

Write-Section "NutriSoft - Instalador completo para Windows"

Write-Host "Pasta do projeto: $BaseDir"
Write-Host "Este instalador irá:"
Write-Host "1. Verificar se o Python existe."
Write-Host "2. Instalar Python via WinGet ou instalador local, se necessário."
Write-Host "3. Criar ambiente virtual .venv."
Write-Host "4. Instalar bibliotecas Python."
Write-Host "5. Validar o ambiente."

Write-Section "Verificando Python"

$PythonCommand = Get-PythonCommand

if ($null -eq $PythonCommand) {
    Write-Host "Python não encontrado." -ForegroundColor Yellow

    $LocalInstaller = Get-ChildItem -Path (Join-Path $BaseDir "installers") -Filter "python-*-amd64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($null -ne $LocalInstaller) {
        Write-Host "Instalador local encontrado: $($LocalInstaller.FullName)" -ForegroundColor Green
        Write-Host "Instalando Python localmente..."
        Start-Process -FilePath $LocalInstaller.FullName -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0" -Wait
    }
    elseif (Test-CommandExists "winget") {
        Write-Host "WinGet encontrado. Instalando Python 3.12 via WinGet..." -ForegroundColor Green
        winget install -e --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements
    }
    else {
        Write-Host ""
        Write-Host "ERRO: Python não encontrado e WinGet não disponível." -ForegroundColor Red
        Write-Host "Solução 1: instale Python 3.12 manualmente pelo site python.org."
        Write-Host "Solução 2: baixe o instalador python-3.12.x-amd64.exe e coloque na pasta installers/."
        Write-Host "Depois execute este instalador novamente."
        exit 1
    }

    Write-Host "Aguardando atualização do ambiente..."
    Start-Sleep -Seconds 5

    $PythonCommand = Get-PythonCommand

    if ($null -eq $PythonCommand) {
        Write-Host ""
        Write-Host "Python foi instalado, mas ainda não apareceu no PATH desta janela." -ForegroundColor Yellow
        Write-Host "Feche este terminal, abra novamente e execute:"
        Write-Host "INSTALAR_COMPLETO_NUTRISOFT_WINDOWS.bat"
        exit 1
    }
}

Write-Host "Python encontrado usando comando: $PythonCommand" -ForegroundColor Green

Write-Section "Criando ambiente virtual"

if (Test-Path ".venv") {
    Write-Host "Ambiente virtual existente encontrado. Mantendo .venv atual."
}
else {
    Write-Host "Criando .venv..."
    Invoke-Python $PythonCommand @("-m", "venv", ".venv")
}

$VenvPython = Join-Path $BaseDir ".venv\Scripts\python.exe"

if (!(Test-Path $VenvPython)) {
    Write-Host "ERRO: não foi possível localizar .venv\Scripts\python.exe" -ForegroundColor Red
    exit 1
}

Write-Section "Instalando bibliotecas"

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

Write-Section "Verificando ambiente NutriSoft"

& $VenvPython scripts\verificar_ambiente.py

Write-Section "Instalação concluída"

Write-Host "Para abrir o NutriSoft, execute:"
Write-Host "INICIAR_NUTRISOFT_WINDOWS.bat" -ForegroundColor Green
Write-Host ""
Write-Host "Endereço local:"
Write-Host "http://localhost:8501" -ForegroundColor Green
