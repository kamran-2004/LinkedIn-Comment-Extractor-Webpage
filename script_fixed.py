from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import time
import csv
from datetime import datetime
import re
import sys
import os
import platform
import subprocess
import traceback

# Get credentials and post URL from command line arguments
EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
POST_URL = sys.argv[3]  # Get the LinkedIn post URL from command line arguments

print("Setting up Chrome WebDriver...")
# Initialize Chrome WebDriver using webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode
options.add_argument('--no-sandbox')  # Required for running in container environments
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.add_argument('--disable-gpu')  # Applicable to windows os only
options.add_argument('--window-size=1920,1080')  # Set a specific window size
options.add_argument('--disable-extensions')  # Disable extensions
options.add_argument('--disable-infobars')  # Disable infobars
options.add_argument('--disable-notifications')  # Disable notifications
options.add_argument('--disable-popup-blocking')  # Disable popup blocking
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')  # Set a common user agent

# Check for Chrome binary location
chrome_binary_locations = [
    "/usr/bin/google-chrome-stable",
    "/usr/bin/google-chrome",
    "/opt/google/chrome/chrome",
    "/usr/bin/chromium",
    # Default Windows location
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
]

chrome_found = False
for chrome_path in chrome_binary_locations:
    if os.path.exists(chrome_path):
        print(f"Chrome binary found at: {chrome_path}")
        options.binary_location = chrome_path
        chrome_found = True
        break

if not chrome_found:
    print("Warning: No Chrome binary found in standard locations")

# Set up Chrome browser
try:
    # Check if we're on Windows
    if platform.system() == "Windows":
        print("Detected Windows system, using Windows WebDriver setup...")
        # On Windows, use the Selenium 4 approach without Service
        driver = webdriver.Chrome(options=options)
    else:
        print(f"Detected {platform.system()} environment...")
        
        # Try multiple approaches to initialize the driver
        driver = None
        exception_messages = []
        
        # Method 1: Try with chromedriver in PATH
        try:
            print("Trying Method 1: Using chromedriver from PATH...")
            driver = webdriver.Chrome(options=options)
            print("Success: Created driver using chromedriver from PATH")
        except Exception as e:
            exception_messages.append(f"Method 1 failed: {str(e)}")
            
            # Method 2: Try to find chromedriver with subprocess
            try:
                print("Trying Method 2: Finding chromedriver with subprocess...")
                result = subprocess.run(["which", "chromedriver"], capture_output=True, text=True)
                chromedriver_path = result.stdout.strip()
                
                if chromedriver_path:
                    print(f"Found chromedriver at: {chromedriver_path}")
                    service = Service(executable_path=chromedriver_path)
                    driver = webdriver.Chrome(service=service, options=options)
                    print("Success: Created driver using located chromedriver")
                else:
                    exception_messages.append("Method 2 failed: chromedriver not found")
            except Exception as e:
                exception_messages.append(f"Method 2 failed: {str(e)}")
                
                # Method 3: Try with chromium
                try:
                    print("Trying Method 3: Using chromium-browser...")
                    options = webdriver.ChromeOptions()
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    
                    if os.path.exists("/usr/bin/chromium"):
                        options.binary_location = "/usr/bin/chromium"
                    
                    driver = webdriver.Chrome(options=options)
                    print("Success: Created driver using chromium")
                except Exception as e:
                    exception_messages.append(f"Method 3 failed: {str(e)}")
        
        # If all methods failed, raise an exception with all error details
        if driver is None:
            error_msg = "All WebDriver initialization methods failed:\n" + "\n".join(exception_messages)
            raise Exception(error_msg)
    
    print("Chrome WebDriver set up successfully!")
except Exception as driver_error:
    print(f"Error setting up Chrome WebDriver: {driver_error}")
    traceback.print_exc()
    sys.exit(1)

# Debug information about the environment
try:
    print(f"Chrome version: {driver.capabilities['browserVersion']}")
    print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
except Exception as cap_error:
    print(f"Could not get browser capabilities: {cap_error}")

try:
    # Open LinkedIn Login Page
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)  # Increased wait time for the page to load

    # Enter email
    email_input = driver.find_element(By.ID, "username")
    email_input.send_keys(EMAIL)

    # Enter password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(PASSWORD)

    # Submit the form
    password_input.send_keys(Keys.RETURN)

    print("Login submitted!")

    # Wait for login to complete - increased wait time
    time.sleep(10)
    
    # Use the provided post URL
    driver.get(POST_URL)
    
    # Wait for the post to load - increased wait time
    time.sleep(8)
    print("Post URL loaded!")
    
    # Scroll down to find the comments section
    print("Scrolling down to find comments section...")
    # Execute JavaScript to scroll down to find comments
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    # Try to change the comment sort order to "Most recent"
    try:
        print("Looking for comment sort dropdown...")
        # Look for the sort dropdown button using various possible selectors
        sort_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'sort') or contains(@class, 'sort')]")
        
        if not sort_buttons:
            sort_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'comments-sort-order')]")
            
        if not sort_buttons:
            sort_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Most relevant') or contains(text(), 'Relevance')]")
            
        if sort_buttons and len(sort_buttons) > 0:
            sort_button = sort_buttons[0]
            print("Sort button found. Clicking to open dropdown...")
            
            # Scroll to make button visible
            driver.execute_script("arguments[0].scrollIntoView(true);", sort_button)
            time.sleep(1)
            
            # Click to open the dropdown
            driver.execute_script("arguments[0].click();", sort_button)
            time.sleep(2)
            
            # Select "Most recent" option
            recent_options = driver.find_elements(By.XPATH, "//li[contains(text(), 'Most recent') or contains(@aria-label, 'recent')]")
            
            if not recent_options:
                recent_options = driver.find_elements(By.XPATH, "//div[contains(text(), 'Most recent') or contains(@aria-label, 'recent')]")
                
            if recent_options and len(recent_options) > 0:
                recent_option = recent_options[0]
                print("'Most recent' option found. Selecting it...")
                driver.execute_script("arguments[0].click();", recent_option)
                time.sleep(3)
                print("Sort order changed to 'Most recent'")
            else:
                print("Could not find 'Most recent' option in dropdown")
        else:
            print("Could not find comment sort button")
    except Exception as sort_error:
        print(f"Error changing sort order: {str(sort_error)}")
    
    # Create unique filename based on current time
    now = datetime.now()
    unique_suffix = now.strftime("-%m-%d-%Y--%H-%M")
    output_filename = f"linkedin-comments{unique_suffix}.csv"
    
    # Create CSV file to store comments
    with open(output_filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Comment", "LinkedIn Profile", "Email", "Time"])
        
        # Find the comments section
        try:
            print("Looking for comments section...")
            comments_section = driver.find_element(By.CLASS_NAME, "comments-comments-list")
            print("Comments section found!")
            
            # Check if there's a "Load more comments" button and click it until all comments are loaded
            load_more_count = 0
            
            while True:  # Keep loading until no more "Load more" buttons are found
                try:
                    # Look for the load more comments button using different selectors
                    load_more_buttons = driver.find_elements(By.CLASS_NAME, "comments-comments-list__load-more-comments-button")
                    
                    if not load_more_buttons:
                        load_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Load more comments')]")
                    
                    if not load_more_buttons:
                        # Try a more generic approach
                        load_more_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'load-more') or contains(text(), 'more')]")
                    
                    if load_more_buttons and len(load_more_buttons) > 0:
                        load_more_button = load_more_buttons[0]
                        print(f"Load more comments button found (attempt {load_more_count+1}). Clicking...")
                        
                        # Scroll to the button to make it visible
                        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                        time.sleep(1)
                        
                        # Click using JavaScript as it's more reliable
                        driver.execute_script("arguments[0].click();", load_more_button)
                        load_more_count += 1
                        
                        # Wait for new comments to load - increased wait time
                        time.sleep(5)
                    else:
                        print("No more 'Load more comments' buttons found.")
                        break
                        
                except Exception as e:
                    print(f"Exception while loading more comments: {str(e)}")
                    break
                    
            print(f"Clicked 'Load more comments' {load_more_count} times. All comments should be loaded.")
            
            # Also try to expand all replies if there are any
            try:
                show_replies_buttons = driver.find_elements(By.CLASS_NAME, "show-prev-replies")
                if show_replies_buttons:
                    print(f"Found {len(show_replies_buttons)} 'Show replies' buttons. Clicking each...")
                    for button in show_replies_buttons:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                        except:
                            pass
            except Exception as reply_error:
                print(f"Error expanding replies: {str(reply_error)}")
            
            # Extract comments based on the correct HTML structure
            print("Looking for the comments container...")
            comment_elements = []
            try:
                # First, find the comments container
                comments_container = driver.find_element(By.CLASS_NAME, "comments-comment-list__container")
                print("Comments container found!")
                
                # Find all comment articles within the container
                comment_elements = comments_container.find_elements(By.TAG_NAME, "article")
                print(f"Found {len(comment_elements)} comments in the container.")
                print(f"Found {len(comment_elements)} comments in total.")
                
            except Exception as container_error:
                print(f"Error finding comments container: {str(container_error)}")
                
                # Try an alternative approach if the standard container isn't found
                try:
                    print("Trying alternative method to find comments...")
                    comment_elements = driver.find_elements(By.XPATH, "//article[contains(@class, 'comments-comment-')]")
                    print(f"Found {len(comment_elements)} comments using alternative method.")
                except Exception as alt_error:
                    print(f"Alternative method also failed: {str(alt_error)}")
                
            if len(comment_elements) > 0:
                print("Extracting comment data...")
                for comment in comment_elements:
                    try:
                        # Extract commenter name
                        name = "Unknown"
                        try:
                            # First try to find the name within the title span
                            name_element = comment.find_element(By.CLASS_NAME, "comments-comment-meta__description-title")
                            name = name_element.text.strip()
                        except:
                            try:
                                # Alternate approach to find the name
                                name_elements = comment.find_elements(By.XPATH, ".//span[contains(@class, 'description-title')]")
                                if name_elements:
                                    name = name_elements[0].text.strip()
                            except:
                                pass
                        
                        # Extract LinkedIn profile URL
                        linkedin_url = "Unknown"
                        try:
                            linkedin_url_element = comment.find_element(By.XPATH, ".//a[contains(@class, 'comments-comment-meta__image-link')]")
                            linkedin_url = linkedin_url_element.get_attribute('href')
                        except:
                            pass
                        
                        # Extract comment text
                        comment_text = "No content"
                        try:
                            # First try to find the comment text with the specific class
                            comment_text_element = comment.find_element(By.CLASS_NAME, "comments-comment-item__main-content")
                            comment_text = comment_text_element.text.strip()
                        except:
                            try:
                                # Alternative selectors for comment text
                                comment_text_elements = comment.find_elements(By.XPATH, ".//span[contains(@class, 'main-content') or contains(@class, 'comment-item__main-content')]")
                                if comment_text_elements:
                                    comment_text = comment_text_elements[0].text.strip()
                                else:
                                    # Try a more generic approach
                                    text_elements = comment.find_elements(By.XPATH, ".//div[contains(@class, 'update-components-text')]")
                                    if text_elements:
                                        comment_text = text_elements[0].text.strip()
                            except:
                                pass
                        
                        # Extract email from comment text
                        email = 'N/A'
                        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', comment_text)
                        if email_match:
                            email = email_match.group(0)
                        
                        # Extract timestamp (if available)
                        comment_time = "Unknown"
                        try:
                            # Find the time element with the specific class
                            time_element = comment.find_element(By.TAG_NAME, "time")
                            comment_time = time_element.text.strip()
                        except:
                            try:
                                # Alternative approach to find timestamp
                                time_elements = comment.find_elements(By.XPATH, ".//time[@class='comments-comment-meta__data']")
                                if time_elements:
                                    comment_time = time_elements[0].text.strip()
                            except:
                                pass
                        
                        # Write to CSV
                        writer.writerow([name, comment_text, linkedin_url, email, comment_time])
                        print(f"Extracted comment from {name}")
                    except Exception as comment_error:
                        print(f"Error extracting a comment: {str(comment_error)}")
                
                print(f"\nSuccessfully extracted {len(comment_elements)} comments and saved to {output_filename}")
            else:
                print("No comments found on this post.")
                
        except Exception as comments_error:
            print(f"Error finding comments section: {str(comments_error)}")

except Exception as e:
    print("Error:", e)
    # More detailed error information
    traceback.print_exc()

finally:
    # Close browser
    driver.quit()
