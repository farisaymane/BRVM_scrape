@echo off
title BRVM Data Extractor
echo ==========================================
echo    BRVM Data Extractor - Demarrage
echo ==========================================
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org
    pause
    exit /b 1
)

echo Python detecte avec succes
echo.

:: Vérifier si le fichier app1.py existe
if not exist "app1.py" (
    echo ERREUR: Le fichier app1.py n'existe pas dans ce repertoire
    echo Veuillez vous assurer que tous les fichiers sont presents
    pause
    exit /b 1
)

:: Vérifier si le fichier sika2_selenium.py existe
if not exist "sika2_selenium.py" (
    echo ERREUR: Le fichier sika2_selenium.py n'existe pas dans ce repertoire
    echo Ce fichier est requis pour le bon fonctionnement de l'application
    pause
    exit /b 1
)

echo Verification des fichiers terminee
echo.

:: Installer les dépendances si requirements.txt existe
if exist "requirements.txt" (
    echo Installation des dependances...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ATTENTION: Certaines dependances n'ont pas pu etre installees
        echo L'application pourrait ne pas fonctionner correctement
        pause
    )
    echo.
)

:: Créer le dossier de téléchargement s'il n'existe pas
if not exist "BRVM_Downloads" (
    mkdir "BRVM_Downloads"
    echo Dossier BRVM_Downloads cree
    echo.
)

:: Lancer l'application
echo Lancement de l'application BRVM Data Extractor...
echo.
echo ==========================================
echo    Application en cours d'execution...
echo    Fermer cette fenetre arretera l'app
echo ==========================================
echo.

python app1.py

:: Gestion des codes de retour
if %errorlevel% equ 0 (
    echo.
    echo Application fermee normalement
) else (
    echo.
    echo L'application s'est fermee avec une erreur (code: %errorlevel%)
    echo Consultez les messages d'erreur ci-dessus pour plus d'informations
)

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul