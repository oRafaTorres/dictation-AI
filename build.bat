@echo off
echo.
echo ========================================
echo   Dictation Tool — Build para .exe
echo ========================================
echo.

echo [1/3] Gerando icon.ico...
python make_icon.py
if errorlevel 1 ( echo ERRO ao gerar icone. & pause & exit /b 1 )

echo.
echo [2/3] Compilando com PyInstaller...
pyinstaller build.spec --clean --noconfirm
if errorlevel 1 ( echo ERRO na compilacao. & pause & exit /b 1 )

echo.
echo [3/3] Copiando .env para dist\DictationTool\...
if exist .env copy /Y .env dist\DictationTool\.env >nul

echo.
echo ========================================
echo   Pronto!
echo   Executavel: dist\DictationTool\DictationTool.exe
echo   Coloque um atalho na area de trabalho
echo   apontando para esse .exe.
echo ========================================
echo.
pause
