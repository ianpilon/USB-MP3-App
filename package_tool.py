import os
import subprocess
import shutil
from pathlib import Path

# Current directory
root_dir = Path(__file__).parent.absolute()

# Create directories for packages
packages_dir = root_dir / "server" / "static_web" / "downloads" / "packages"
os.makedirs(packages_dir, exist_ok=True)

# Source script
source_script = root_dir / "server" / "static_web" / "downloads" / "dj_usb_tool.py"

def create_windows_package():
    """Create Windows executable and installer"""
    print("Building Windows package...")
    
    # Windows directory
    win_dir = packages_dir / "windows"
    os.makedirs(win_dir, exist_ok=True)
    
    # Create batch file wrapper
    batch_file = win_dir / "DJ_USB_Tool.bat"
    with open(batch_file, "w") as f:
        f.write("@echo off\n")
        f.write("echo Starting DJ USB Tool...\n")
        f.write("python \"%~dp0dj_usb_tool.py\" sync\n")
        f.write("pause\n")
    
    # Copy Python script
    shutil.copy(source_script, win_dir / "dj_usb_tool.py")
    
    # Create README
    with open(win_dir / "README.txt", "w") as f:
        f.write("DJ USB Tool - Windows Version\n")
        f.write("===========================\n\n")
        f.write("Instructions:\n")
        f.write("1. Copy this entire folder to your USB drive\n")
        f.write("2. Double-click on DJ_USB_Tool.bat to start syncing\n\n")
        f.write("Requirements:\n")
        f.write("- Python 3.6 or higher installed\n")
        f.write("- Python 'requests' package (run 'pip install requests' if needed)\n")
    
    # Create ZIP file
    zip_file = packages_dir / "DJ_USB_Tool_Windows.zip"
    if os.path.exists(zip_file):
        os.remove(zip_file)
    
    shutil.make_archive(packages_dir / "DJ_USB_Tool_Windows", "zip", win_dir)
    print(f"Windows package created: {zip_file}")
    return f"/web/downloads/packages/DJ_USB_Tool_Windows.zip"

def create_mac_package():
    """Create macOS package"""
    print("Building macOS package...")
    
    # Mac directory
    mac_dir = packages_dir / "mac"
    os.makedirs(mac_dir, exist_ok=True)
    
    # Create shell script wrapper
    shell_script = mac_dir / "DJ_USB_Tool.command"
    with open(shell_script, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("cd \"$(dirname \"$0\")\"\n")
        f.write("echo \"Starting DJ USB Tool...\"\n")
        f.write("python3 dj_usb_tool.py sync\n")
        f.write("echo \"Press Enter to exit...\"\n")
        f.write("read\n")
    
    # Make shell script executable
    os.chmod(shell_script, 0o755)
    
    # Copy Python script
    shutil.copy(source_script, mac_dir / "dj_usb_tool.py")
    
    # Create README
    with open(mac_dir / "README.txt", "w") as f:
        f.write("DJ USB Tool - macOS Version\n")
        f.write("=========================\n\n")
        f.write("Instructions:\n")
        f.write("1. Copy this entire folder to your USB drive\n")
        f.write("2. Double-click on DJ_USB_Tool.command to start syncing\n"
                "   (If it doesn't open, right-click and select Open)\n\n")
        f.write("Requirements:\n")
        f.write("- Python 3.6 or higher installed\n")
        f.write("- Python 'requests' package (run 'pip3 install requests' if needed)\n")
    
    # Create ZIP file
    zip_file = packages_dir / "DJ_USB_Tool_macOS.zip"
    if os.path.exists(zip_file):
        os.remove(zip_file)
    
    shutil.make_archive(packages_dir / "DJ_USB_Tool_macOS", "zip", mac_dir)
    print(f"macOS package created: {zip_file}")
    return f"/web/downloads/packages/DJ_USB_Tool_macOS.zip"

def create_linux_package():
    """Create Linux package"""
    print("Building Linux package...")
    
    # Linux directory
    linux_dir = packages_dir / "linux"
    os.makedirs(linux_dir, exist_ok=True)
    
    # Create shell script wrapper
    shell_script = linux_dir / "DJ_USB_Tool.sh"
    with open(shell_script, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("cd \"$(dirname \"$0\")\"\n")
        f.write("echo \"Starting DJ USB Tool...\"\n")
        f.write("python3 dj_usb_tool.py sync\n")
        f.write("echo \"Press Enter to exit...\"\n")
        f.write("read\n")
    
    # Make shell script executable
    os.chmod(shell_script, 0o755)
    
    # Copy Python script
    shutil.copy(source_script, linux_dir / "dj_usb_tool.py")
    
    # Create README
    with open(linux_dir / "README.txt", "w") as f:
        f.write("DJ USB Tool - Linux Version\n")
        f.write("========================\n\n")
        f.write("Instructions:\n")
        f.write("1. Copy this entire folder to your USB drive\n")
        f.write("2. Right-click DJ_USB_Tool.sh and select 'Run as Program'\n")
        f.write("   or open terminal and run: ./DJ_USB_Tool.sh\n\n")
        f.write("Requirements:\n")
        f.write("- Python 3.6 or higher installed\n")
        f.write("- Python 'requests' package (run 'pip3 install requests' if needed)\n")
    
    # Create ZIP file
    zip_file = packages_dir / "DJ_USB_Tool_Linux.zip"
    if os.path.exists(zip_file):
        os.remove(zip_file)
    
    shutil.make_archive(packages_dir / "DJ_USB_Tool_Linux", "zip", linux_dir)
    print(f"Linux package created: {zip_file}")
    return f"/web/downloads/packages/DJ_USB_Tool_Linux.zip"

def main():
    print("Creating platform packages...")
    
    # Create packages for all platforms
    win_path = create_windows_package()
    mac_path = create_mac_package()
    linux_path = create_linux_package()
    
    print("\nAll packages created successfully!")
    print(f"Windows: {win_path}")
    print(f"macOS: {mac_path}")
    print(f"Linux: {linux_path}")

if __name__ == "__main__":
    main()
