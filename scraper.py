import time
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Environment Variables
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "twitter_scraper"
COLLECTION_NAME = "trending_topics"
PROXY = "103.70.206.65:59311"

# XPaths for login and scraping
email_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'
password_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'
login_xpath_click = '//*[@id ="react-root"]/div/div/div[2]/main/div/div/div[1]/form/div/div[3]/div/div'
next_xpath_click = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]'
trending_topics_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div'


def setup_mongo_client():
    """Setup MongoDB client."""
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]


def setup_driver(proxy=None):
    """Setup Selenium WebDriver with proxy."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % proxy)

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def login_to_twitter(driver, username, password):
    """Login to Twitter using provided credentials."""
    driver.get("https://x.com/i/flow/login")
    time.sleep(5)
    try:
        email_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, email_xpath))
        )
        email_element.send_keys(username)

        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_xpath_click))
        )
        next_button.click()

        password_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        password_element.send_keys(password)

        login_button_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, login_xpath_click))
        )
        login_button_element.click()
    except Exception as e:
        raise Exception(f"Login failed: {e}")


def fetch_trending_topics(proxy=None):
    """Fetch trending topics from Twitter and store in MongoDB."""
    print("before driver")
    driver = setup_driver(proxy)
    print("after driver")
    collection = setup_mongo_client()
    try:
        login_to_twitter(driver, TWITTER_USERNAME, TWITTER_PASSWORD)

        # Navigate to the home page
        driver.get("https://twitter.com/home")
        time.sleep(5)

        # Extract trending topics
        trends = driver.find_elements(By.XPATH, trending_topics_xpath)
        top_trends = [trend.text for trend in trends[:5]]

        # Capture additional information
        unique_id = str(uuid.uuid4())
        ip_address = proxy.split(":")[0] if proxy else "No Proxy"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare data for MongoDB
        record = {
            "_id": unique_id,
            "trend1": top_trends[0] if len(top_trends) > 0 else "",
            "trend2": top_trends[1] if len(top_trends) > 1 else "",
            "trend3": top_trends[2] if len(top_trends) > 2 else "",
            "trend4": top_trends[3] if len(top_trends) > 3 else "",
            "trend5": top_trends[4] if len(top_trends) > 4 else "",
            "timestamp": timestamp,
            "ip_address": ip_address,
        }

        # Insert into MongoDB
        collection.insert_one(record)
        print("Trending topics saved to MongoDB:", record)

        return record
    except Exception as e:
        raise Exception(f"Error fetching trends: {e}")
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    fetch_trending_topics(PROXY)
