#!/usr/bin/env bash
# Exit on error
set -o errexit

# Installing Google Chrome for Selenium
echo "Installing Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update -y
apt-get install -y google-chrome-stable

# Print Chrome version for debugging
echo "Chrome version:"
google-chrome --version

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!" 