from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import platform

print(f"Running test on platform: {platform.system()}")

# Set up Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

try:
    print("Initializing Chrome WebDriver...")
    driver = webdriver.Chrome(options=options)
    print("Chrome WebDriver initialized successfully!")
    
    # Print capabilities for debugging
    print(f"Chrome version: {driver.capabilities['browserVersion']}")
    print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
    
    # Test navigation
    print("Navigating to google.com...")
    driver.get("https://www.google.com")
    print(f"Page title: {driver.title}")
    
    # Take a screenshot as proof
    driver.save_screenshot("test_screenshot.png")
    print("Screenshot saved as test_screenshot.png")
    
    # Close the browser
    driver.quit()
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc() 