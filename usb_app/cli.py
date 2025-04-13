import os
import sys
import click
import logging
from pathlib import Path
from usb_manager import USBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_SERVER = "https://dj-usb-server-usb-mp3-app.onrender.com"

@click.group()
def cli():
    """DJ USB Virtual Drive Manager"""
    pass

@cli.command()
@click.argument('usb_path', type=click.Path(exists=True))
@click.option('--server', '-s', default=DEFAULT_SERVER,
              help='URL of the DJ USB server')
def init(usb_path: str, server: str):
    """Initialize a new DJ USB drive at USB_PATH"""
    try:
        manager = USBManager(usb_path, server)
        if manager.initialize_drive():
            click.echo(f"Successfully initialized DJ USB drive at {usb_path}")
            click.echo(f"Server: {server}")
        else:
            click.echo("Failed to initialize drive")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize drive: {e}")
        sys.exit(1)

@cli.command()
@click.argument('usb_path', type=click.Path(exists=True))
@click.option('--server', '-s', default=DEFAULT_SERVER,
              help='URL of the DJ USB server')
def sync(usb_path: str, server: str):
    """Sync USB drive with server"""
    try:
        manager = USBManager(usb_path, server)
        if manager.sync():
            songs = manager.get_song_list()
            click.echo(f"Successfully synced {len(songs)} songs")
            for song in songs:
                click.echo(f"  {song['filename']}")
        else:
            click.echo("Failed to sync drive")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to sync drive: {e}")
        sys.exit(1)

@cli.command()
@click.argument('usb_path', type=click.Path(exists=True))
def status(usb_path: str):
    """Show USB drive status"""
    try:
        manager = USBManager(usb_path, DEFAULT_SERVER)
        songs = manager.get_song_list()
        click.echo(f"DJ USB Drive at {usb_path}")
        click.echo(f"Total songs: {len(songs)}")
        click.echo("\nSongs:")
        for song in songs:
            last_played = song.get('last_played', 'Never')
            cached = '✓' if song.get('cached', False) else ' '
            click.echo(f"  [{cached}] {song['filename']} (Last played: {last_played})")
    except Exception as e:
        logger.error(f"Failed to get drive status: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()
