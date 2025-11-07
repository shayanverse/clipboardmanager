"""
Build executable using PyInstaller
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller"""
    
    # Create assets if they don't exist
    from create_assets import create_assets
    create_assets()
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # PyInstaller configuration
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('assets/logo.png', 'assets')
    ],
    hiddenimports=[
        'pymongo',
        'pymongo.srv_resolver',
        'pymongo.aws',
        'pymongo.dns',
        'pymongo.pyopenssl_context',
        'pymongo.ssl_context',
        'pymongo.ssl_support',
        'bson',
        'bson._cbson',
        'dnspython',
        'urllib3',
        'requests',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'tkinter',
        'pyperclip'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ThoughtLink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
"""
    
    # Write spec file
    with open("thoughtlink.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    try:
        print("Building executable with PyInstaller...")
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "--noconfirm",
            "thoughtlink.spec"
        ], check=True)
        
        print("Build completed successfully!")
        print(f"Executable location: dist/ThoughtLink/ThoughtLink.exe")
        
        # Clean up spec file
        os.remove("thoughtlink.spec")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe()