@echo off
echo.
echo === Dictation Tool — Instalando dependencias ===
echo.
pip install -r requirements.txt
echo.
if %errorlevel% == 0 (
    echo === Instalacao concluida! ===
    echo.
    echo O projeto esta pronto para uso.
) else (
    echo === ERRO na instalacao. Verifique se o Python esta no PATH. ===
)
echo.
pause
