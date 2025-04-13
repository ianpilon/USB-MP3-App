import PyInstaller.__main__
import os
import shutil
import sys
from pathlib import Path

# Get the script directory
script_dir = Path(__file__).parent.absolute()

# Create a dist directory if it doesn't exist
dist_dir = script_dir / "dist"
dist_dir.mkdir(exist_ok=True)

# Version number
version = "1.0.0"

# Define paths
output_dir = script_dir / "build" / "usb_tool"
output_file = f"DJ_USB_Tool-{version}"

# Build the executable using PyInstaller
def build_executable():
    print(f"Building USB Tool v{version}...")
    
    # Clean any previous build
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Define PyInstaller arguments
    args = [
        "--name=dj_usb_tool",
        "--onefile",
        "--windowed",
        "--icon=server/static_web/favicon.ico" if os.path.exists("server/static_web/favicon.ico") else "",
        "--add-data=requirements.txt:.",
        "--distpath=" + str(output_dir),
        "usb_app/cli.py",
    ]
    
    # Remove empty arguments
    args = [arg for arg in args if arg]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print(f"Executable built at {output_dir / 'dj_usb_tool'}{'.exe' if sys.platform == 'win32' else ''}")

# Create a distribution zip file
def create_distribution():
    print("Creating distribution package...")
    
    # Create a directory for the distribution package
    package_dir = output_dir / output_file
    package_dir.mkdir(exist_ok=True)
    
    # Copy the executable to the package directory
    executable = output_dir / f"dj_usb_tool{'.exe' if sys.platform == 'win32' else ''}"
    shutil.copy(executable, package_dir)
    
    # Create a README.txt file
    with open(package_dir / "README.txt", "w") as f:
        f.write(f"\nDJ USB Tool v{version}\n")
        f.write("=================\n\n")
        f.write("This tool helps you sync music from your DJ USB Manager account to your USB drive.\n\n")
        f.write("Instructions:\n")
        f.write("1. Copy this entire folder to your USB drive\n")
        f.write("2. Plug your USB drive into your computer\n")
        f.write("3. Run the dj_usb_tool executable\n")
        f.write("4. Follow the on-screen instructions\n\n")
        f.write("For more information, visit https://dj-usb-server-usb-mp3-app.onrender.com/\n")
    
    # Create a zip file
    print(f"Creating zip file: {dist_dir / (output_file + '.zip')}")
    shutil.make_archive(str(dist_dir / output_file), 'zip', output_dir, output_file)
    
    print(f"Distribution package created at {dist_dir / (output_file + '.zip')}")

# Main function
def main():
    # Build the executable
    build_executable()
    
    # Create the distribution package
    create_distribution()
    
    print("\nBuild completed successfully!")
    print(f"USB Tool package available at: {dist_dir / (output_file + '.zip')}")

if __name__ == "__main__":
    main()
