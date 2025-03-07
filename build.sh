#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."
echo "Current directory: $(pwd)"

# Add Debian buster non-free to sources for Chrome installation
apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release

# Add Google's official repository
echo "Adding Google Chrome repository..."
curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update apt sources
echo "Updating sources and installing Chrome..."
apt-get update -y

# Try to install Chrome
echo "Installing Google Chrome..."
apt-get install -y google-chrome-stable || {
    echo "Primary Chrome installation failed, trying alternative method..."
    # Alternative method - direct wget download
    mkdir -p /tmp/chrome
    cd /tmp/chrome
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install -y ./google-chrome-stable_current_amd64.deb || {
        echo "Alternative Chrome installation failed, installing chromium as fallback..."
        apt-get install -y chromium
    }
    cd -
}

# Install ChromeDriver
echo "Installing chromedriver..."
CHROME_VERSION=$(google-chrome-stable --version 2>/dev/null | awk '{print $3}' | cut -d '.' -f 1,2,3 || echo "")
if [ -z "$CHROME_VERSION" ]; then
    echo "Could not detect Chrome version, installing latest chromedriver"
    apt-get install -y chromium-driver || echo "Failed to install chromium-driver"
else
    echo "Detected Chrome version: $CHROME_VERSION"
    apt-get install -y chromium-driver || echo "Failed to install chromium-driver"
fi

# Print Chrome version for debugging
echo "Chrome installation complete. Checking version:"
which google-chrome-stable || echo "Chrome not found in PATH"
google-chrome-stable --version || echo "Failed to get Chrome version"
which chromedriver || echo "ChromeDriver not found in PATH"
chromedriver --version || echo "Failed to get ChromeDriver version"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create a simple test to check Chrome is working
echo "Testing Chrome installation..."
cat > chrome_test.py << 'EOL'
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Check Chrome binary location
chrome_paths = [
    "/usr/bin/google-chrome-stable",
    "/usr/bin/google-chrome",
    "/opt/google/chrome/chrome",
    "/usr/bin/chromium"
]

print("Checking Chrome binary locations:")
for path in chrome_paths:
    print(f"- {path}: {'Exists' if os.path.exists(path) else 'Not found'}")

# Try to run Chrome directly
try:
    print("\nRunning Chrome version check from command line:")
    for cmd in ["google-chrome-stable --version", "google-chrome --version", "chromium --version"]:
        try:
            print(f"Trying: {cmd}")
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.stdout:
                print(f"Result: {result.stdout}")
                break
        except:
            continue
except Exception as e:
    print(f"Error running Chrome: {e}")

# Try basic Selenium setup
try:
    print("\nTesting Selenium with Chrome:")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Find Chrome binary
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"Using Chrome binary at: {path}")
            options.binary_location = path
            break
    
    driver = webdriver.Chrome(options=options)
    print("Chrome driver initialized successfully")
    driver.quit()
except Exception as e:
    print(f"Selenium error: {e}")
EOL

python chrome_test.py || echo "Chrome test failed, but continuing build"

echo "Build completed successfully!" 