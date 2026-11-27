@echo off
chcp 65001 >nul
cd /d "%~dp0"

for /f "delims=" %%I in ('git rev-parse --git-path hooks/pre-commit') do set "HOOK_PATH=%%I"
if not defined HOOK_PATH exit /b 1
if exist "%HOOK_PATH%" (
    fc /b ".githooks\pre-commit" "%HOOK_PATH%" >nul
    if errorlevel 1 (
        echo Ja existe um hook diferente. Integre a verificacao sem sobrescrever o hook atual.
        exit /b 1
    )
    echo Hook de seguranca ja instalado.
    exit /b 0
)
copy /b ".githooks\pre-commit" "%HOOK_PATH%" >nul
if errorlevel 1 exit /b 1
echo Hook de seguranca instalado.
