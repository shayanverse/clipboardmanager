@echo off
echo Setting up Thought-Link...


python -m venv thoughtlink_env
call thoughtlink_env\Scripts\activate.bat


pip install -r requirements.txt


python create_assets.py

echo Setup completed!
echo.
echo To run the application:
echo thoughtlink_env\Scripts\activate.bat
echo python main.py
echo.
echo To build executable:
echo python build_exe.py
pause