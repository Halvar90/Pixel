#!/bin/bash

# Railway startup script for additional configuration
echo "Starting Pixel Discord Bot on Railway..."

# Set timezone (optional)
export TZ=Europe/Berlin

# Start the bot
exec python bot.py
