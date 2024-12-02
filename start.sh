#!/bin/sh

# Set default resolution if not provided
RESOLUTION=${RESOLUTION:-1200x800x24}

# Extract width, height and depth from resolution
WIDTH=$(echo $RESOLUTION | cut -d'x' -f1)
HEIGHT=$(echo $RESOLUTION | cut -d'x' -f2)
DEPTH=$(echo $RESOLUTION | cut -d'x' -f3)

# Create ffmpeg resolution (without depth)
FFMPEG_RESOLUTION="${WIDTH}x${HEIGHT}"

# Replace placeholders in supervisord config
sed -i "s|RESOLUTION_PLACEHOLDER|$RESOLUTION|g" /etc/supervisor.d/supervisord.ini
sed -i "s|FFMPEG_PLACEHOLDER|$FFMPEG_RESOLUTION|g" /etc/supervisor.d/supervisord.ini
sed -i "s|WIDTH_PLACEHOLDER|$WIDTH|g" /etc/supervisor.d/supervisord.ini
sed -i "s|HEIGHT_PLACEHOLDER|$HEIGHT|g" /etc/supervisor.d/supervisord.ini

# Start supervisord
exec /usr/bin/supervisord -n -c /etc/supervisor.d/supervisord.ini