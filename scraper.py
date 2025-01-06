from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.firefox.service import Service  # type: ignore
from selenium.webdriver.firefox.options import Options  # type: ignore
from webdriver_manager.firefox import GeckoDriverManager  # type: ignore
from datetime import datetime
import uuid
import requests 
from pymongo import MongoClient  # type: ignore
import json
from config import (
    MONGODB_URI,
    DATABASE_NAME,
    COLLECTION_NAME,
    PROXYMESH_USERNAME,
    PROXYMESH_PASSWORD,
    PROXYMESH_HOST,
    TWITTER_USERNAME,
    TWITTER_PASSWORD
)

def setup_driver(proxy_host):
    print("Setting up Firefox driver...")
    options = Options()
    
    # Configure proxy
    proxy = f"http://{PROXYMESH_USERNAME}:{PROXYMESH_PASSWORD}@{proxy_host}"
    options.add_argument(f'--proxy={proxy}')
    
    # Add additional options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')

    print("Initializing Firefox driver...")
    service = Service(GeckoDriverManager().install())
    
    try:
        driver = webdriver.Firefox(service=service, options=options)
        print("Firefox driver setup successful!")
        return driver
    except Exception as e:
        print(f"Driver setup error: {str(e)}")
        raise

def login_to_twitter(driver):
    try:
        print("Attempting to access Twitter login page...")
        driver.get('https://twitter.com/login')
        
        print("Waiting for username field...")
        username_input = WebDriverWait(driver, 20).until( 
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
        )
        print("Found username field, entering username...")
        username_input.send_keys(TWITTER_USERNAME)
        
        print("Looking for Next button...")
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
        )
        next_button.click()
        
        print("Waiting for password field...")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        print("Found password field, entering password...")
        password_input.send_keys(TWITTER_PASSWORD)
        
        print("Looking for Login button...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        )
        login_button.click()
        
        print("Waiting for login to complete...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
        )
        print("Login successful!")
        
    except Exception as e:
        print(f"Detailed login error: {str(e)}")
        try:
            driver.save_screenshot("login_error.png")
            print("Error screenshot saved as login_error.png")
        except:
            print("Could not save error screenshot")
        raise

def fetch_trending_topics(driver, retries=3):
    for attempt in range(retries):
        try:
            print("Waiting for trends to load...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='trend']"))
            )

            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Show more']"))
                )
                show_more_button.click()
                print("Clicked on the 'Show more' button to load additional trends...")
                
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='trend']"))
                )
            except Exception as e:
                print(f"'Show more' button not found or could not be clicked: {e}")

            trends = driver.find_elements(By.CSS_SELECTOR, "[data-testid='trend']")
            print(f"Found {len(trends)} trends after clicking 'Show more': {[trend.text for trend in trends]}")
            
            result = []
            for i, trend in enumerate(trends[:5]):
                try:
                    trend_text = trend.text.split('\n')[0]
                    print(f"Trend {i + 1}: {trend_text}")
                    result.append(trend_text)
                except:
                    result.append(f"Error reading trend {i + 1}")

            if len(result) < 5:
                print("Warning: Fewer than 5 trends found. Returning available trends.")
                
            return result[:5]

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                print("Retrying to fetch trends...")
            else:
                print("All attempts to fetch trends failed.")
                try:
                    driver.save_screenshot("trends_error.png")
                    print("Error screenshot saved as trends_error.png")
                except:
                    print("Could not save error screenshot")
                return ["Error fetching trend"] * 5

def save_to_mongodb(trends, ip_address):
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        record = {
            "_id": str(uuid.uuid4()),
            "nameoftrend1": trends[0],
            "nameoftrend2": trends[1],
            "nameoftrend3": trends[2],
            "nameoftrend4": trends[3],
            "nameoftrend5": trends[4],
            "timestamp": datetime.now(),
            "ip_address": ip_address
        }
        
        collection.insert_one(record)
        return record
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        raise
    finally:
        client.close()

def scrape_trends():
    driver = None
    try:
        driver = setup_driver(PROXYMESH_HOST)
        login_to_twitter(driver)
        trends = fetch_trending_topics(driver)
        
        # Fetch IP address directly using requests
        try:
            response = requests.get('https://api.ipify.org?format=json', proxies={"http": f"http://{PROXYMESH_USERNAME}:{PROXYMESH_PASSWORD}@{PROXYMESH_HOST}"})
            ip_response = response.json()
            ip_address = ip_response['ip'] if response.status_code == 200 else 'IP Fetch Failed'
        except Exception as e:
            print(f"Error fetching IP address: {e}")
            ip_address = 'IP Fetch Failed'
        
        record = save_to_mongodb(trends, ip_address)
        return record
    except Exception as e:
        print(f"Error in scrape_trends: {e}")
        return None
    finally:
        if driver:
            driver.quit()
