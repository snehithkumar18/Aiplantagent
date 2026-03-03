@echo off
echo ==========================================
echo Saving and Pushing changes to GitHub...
echo ==========================================

REM Add all changes to git
git add .

REM Prompt the user for a commit message (or use a default one)
set /p commitMsg="Enter commit message (or press enter for default 'Update'): "
if "%commitMsg%"=="" set commitMsg=Update files

REM Commit the changes
git commit -m "%commitMsg%"

REM Push changes to GitHub (sets upstream branch to origin main if not set)
git push -u origin main

echo.
echo ==========================================
echo Done! Your changes have been saved to GitHub.
echo ==========================================
pause
