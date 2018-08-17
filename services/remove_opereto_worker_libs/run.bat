@echo off
rmdir /q /s %opereto_home%\operetovenv && (
python -u run.py
exit %errorlevel%
) || (
echo "Failed to remove. Please remove the following libraries manually:"
    echo %opereto_home%\operetovenv
    exit 2;
)
