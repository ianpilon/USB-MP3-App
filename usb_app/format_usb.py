import os
import sys
import click
import shutil
from pathlib import Path

def is_removable_drive(path: str) -> bool:
    """Check if the given path is likely a removable drive."""
    if sys.platform == 'darwin':  # macOS
        return path.startswith('/Volumes/') and not path == '/Volumes/Macintosh HD'
    else:  # Linux
        return path.startswith('/media/')

@click.command()
@click.argument('drive_path', type=click.Path(exists=True))
def format_drive(drive_path: str):
    """Format a USB drive for use with DJ-USB-App."""
    
    drive_path = os.path.abspath(drive_path)
    
    if not is_removable_drive(drive_path):
        click.echo("Warning: This doesn't look like a removable drive.")
        if not click.confirm("Are you sure you want to continue?"):
            sys.exit(1)
    
    click.echo(f"Formatting drive at {drive_path}")
    click.echo("This will:")
    click.echo("1. Create a Music directory")
    click.echo("2. Set up the DJ app configuration")
    click.echo("3. Initialize sync settings")
    
    if not click.confirm("Do you want to continue?"):
        sys.exit(0)
    
    try:
        # Create Music directory
        music_dir = Path(drive_path) / "Music"
        music_dir.mkdir(exist_ok=True)
        
        # Create app directory
        app_dir = Path(drive_path) / ".dj-app"
        app_dir.mkdir(exist_ok=True)
        
        # Create README
        readme = Path(drive_path) / "README.txt"
        with open(readme, 'w') as f:
            f.write("""DJ USB Drive

This drive is managed by DJ-USB-App. Your music files will appear in the Music directory.
Do not modify files directly as they are managed by the sync system.

To use:
1. Run 'python usb_app/cli.py init /path/to/drive'
2. Run 'python usb_app/cli.py sync /path/to/drive' to download songs
3. Run 'python usb_app/cli.py status /path/to/drive' to check status

The drive will work with Serato DJ and other DJ software.""")
        
        click.echo("\nDrive formatted successfully!")
        click.echo(f"\nNext steps:")
        click.echo(f"1. Initialize the drive:")
        click.echo(f"   python usb_app/cli.py init {drive_path}")
        click.echo(f"2. Sync your music:")
        click.echo(f"   python usb_app/cli.py sync {drive_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    format_drive()
