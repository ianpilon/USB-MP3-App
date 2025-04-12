#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_spec_file():
    """Create a PyInstaller spec file with custom settings."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['usb_app/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('usb_app/*.py', 'usb_app')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    name='usb-mp3-tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    with open('usb_mp3_tool.spec', 'w') as f:
        f.write(spec_content)

def clean_build_artifacts():
    """Clean up previous build artifacts."""
    paths_to_remove = ['build', 'dist', '*.spec']
    for path in paths_to_remove:
        if '*' in path:
            # Handle wildcards
            for p in Path('.').glob(path):
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)
        else:
            p = Path(path)
            if p.exists():
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)

def build_installer():
    """Build the installer for the current platform."""
    try:
        # Clean up previous builds
        clean_build_artifacts()
        
        # Create spec file
        create_spec_file()
        
        # Build the executable
        subprocess.run(['pyinstaller', '--name=usb-mp3-tool', '--onefile', 'usb_app/cli.py'], check=True)
        
        # Get the platform-specific name
        if sys.platform.startswith('win'):
            platform_name = 'windows'
        elif sys.platform.startswith('darwin'):
            platform_name = 'macos'
        else:
            platform_name = 'linux'
        
        # Create the distribution directory if it doesn't exist
        dist_dir = Path('dist')
        dist_dir.mkdir(exist_ok=True)
        
        # Move the built executable to a platform-specific name
        executable = dist_dir / 'usb-mp3-tool'
        if sys.platform.startswith('win'):
            executable = executable.with_suffix('.exe')
        
        if executable.exists():
            new_name = f'usb-mp3-tool-{platform_name}'
            if sys.platform.startswith('win'):
                new_name += '.exe'
            new_path = dist_dir / new_name
            shutil.move(str(executable), str(new_path))
            print(f'Created installer: {new_path}')
            return True
        else:
            print('Error: Build failed - executable not found')
            return False
    except Exception as e:
        print(f'Error during build: {e}')
        return False

def main():
    """Main entry point."""
    try:
        build_installer()
    except Exception as e:
        print(f'Error building installer: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
