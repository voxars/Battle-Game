@echo off
echo ============================================
echo  Bataille de Lignes sur Cercle - v1.0
echo  Creation d'executable
echo ============================================
echo.

echo Suppression des anciens fichiers de build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Creation de l'executable...
python -m PyInstaller --onefile --windowed --name "Bataille-Cercle-v1.0" battle_circle.py

echo.
if exist "dist\Bataille-Cercle-v1.0.exe" (
    echo ✅ Executable cree avec succes !
    echo.
    echo Copie sur le bureau...
    copy "dist\Bataille-Cercle-v1.0.exe" "%USERPROFILE%\Desktop\" >nul
    if %errorlevel%==0 (
        echo ✅ Executable copie sur le bureau !
        echo.
        echo 📂 Fichier: %USERPROFILE%\Desktop\Bataille-Cercle-v1.0.exe
        echo 💾 Taille: 
        dir "%USERPROFILE%\Desktop\Bataille-Cercle-v1.0.exe" | find "Bataille-Cercle-v1.0.exe"
    ) else (
        echo ❌ Erreur lors de la copie sur le bureau
    )
) else (
    echo ❌ Erreur lors de la creation de l'executable
)

echo.
echo Appuyez sur une touche pour continuer...
pause >nul