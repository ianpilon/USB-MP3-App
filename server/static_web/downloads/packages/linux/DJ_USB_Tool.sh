#!/bin/bash
cd "$(dirname "$0")"
echo "Starting DJ USB Tool..."
python3 dj_usb_tool.py sync
echo "Press Enter to exit..."
read
