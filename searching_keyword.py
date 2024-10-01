
import requests
from bs4 import BeautifulSoup
import re
from database_handler import *
from config import *
import time
import retry
import multiprocessing
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from driver import Driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

ua = UserAgent()

data = get_website_from_db(niche)
url = data[0][1]
id = data[0][0]

# Headers to avoid being blocked
def get_headers():
    return {'User-Agent': ua.random}

def check_website(url, id):
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers)
        time.sleep(5)
        
        if response.status_code == 200:
            print(f"Website {url} and id {id} is accessible.")
            return True
        else:
            print(f"Website {url} and id {id} returned status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Website {url} is not accessible. Error: {e}")
        return False

EXCLUDED_EXTENSIONS = [".pdf", ".jpg", ".zip", ".mp4", ".webp", ".webm", 
                       ".json", ".xml", ".csv", ".xlsx", ".doc", ".docx", 
                       ".jpeg", ".png", ".ico", ".css"]

def get_internal_links_selenium(url, domain):
    try:
        driver, wait = Driver(10)  
        
        driver.get(url)
        
        # Wait for a specific element to be present
        try:
            wait.until(lambda d: d.find_element(By.TAG_NAME, 'a'))  # Wait for at least one <a> tag
        except TimeoutException:
            print(f"Timeout: No links found on {url} within the specified time.")
            return set()  # Return an empty set to indicate no internal links found
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()  # Close the browser once the page is loaded

        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/') or domain in href:
                full_url = requests.compat.urljoin(url, href)
                if not any(full_url.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                    links.add(full_url)

        if not links:
            print(f"No internal links found on {url}.")
        return links
    except Exception as e:
        print(f"Error occurred while fetching internal links using Selenium for {url}: {e}")
        return set() 

def get_internal_links(url, domain):
    retries = 0
    while retries < 3:
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=20)  # Set a timeout here too
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Exclude mailto links and other unwanted extensions
                if href.startswith('mailto:'):
                    continue
                if href.startswith('/') or domain in href:
                    full_url = requests.compat.urljoin(url, href)
                    if not any(full_url.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                        links.add(full_url)

            print(f"Found internal links: {links}")
            return links

        except requests.exceptions.RequestException as e:
            retries += 1
            print(f"Error fetching links (attempt {retries}/{3}): {str(e)}")
            if retries < 3:
                print(f"Retrying in {5} seconds...")
                time.sleep(5)

    print(f"Max retries reached. Unable to access website {url}")
    update_website_error_flag(id=id, niche=niche)
    return "Website not accessible after retries."

def search_keywords_in_page(url, keywords):
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=20)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an error for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ')
        
        found_keywords = {}
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", page_text, re.IGNORECASE):
                found_keywords[keyword] = 1
            else:
                found_keywords[keyword] = 0

        return found_keywords
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for {url}: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred for {url}: {conn_err}")
    except requests.exceptions.Timeout:
        print(f"Timeout occurred for {url}.")
    except Exception as e:
        print(f"Error fetching page {url}: {str(e)}")
    return {}

# Move process_link to a top-level function
def process_link(args):
    link, keywords = args
    try:
        keyword_results = search_keywords_in_page(link, keywords)
        return link, keyword_results
    except Exception as e:
        print(f"Error processing link {link}: {str(e)}")
        return link, {}

def crawl_and_search(url, keywords):
    domain = requests.compat.urlparse(url).netloc
    internal_links = get_internal_links(url, domain)

    if not internal_links or isinstance(internal_links, str):
        print(f"Error retrieving internal links: {internal_links}")
        print("Trying to get internal links using Selenium as a fallback.")
        internal_links = get_internal_links_selenium(url, domain)

        if not internal_links:
            print("Failed to retrieve internal links using both methods.")
            update_website_error_flag(id=id, niche=niche)
            return False

    # Track distinct keywords found
    distinct_keywords_found = set()

    # Check keywords in the main page content first
    main_page_keywords = search_keywords_in_page(url, keywords)
    distinct_keywords_found.update([keyword for keyword, found in main_page_keywords.items() if found])

    # Proceed to check internal links only if not enough keywords found
    results = {}
    with multiprocessing.Pool() as pool:
        result_list = pool.map(process_link, [(link, keywords) for link in internal_links])

    for link, keyword_status in result_list:
        results[link] = keyword_status
        distinct_keywords_found.update([keyword for keyword, found in keyword_status.items() if found])

    print(f"Distinct keywords found in {url}: {distinct_keywords_found}")

    # Only update the training flag if at least 3 distinct keywords are found
    if len(distinct_keywords_found) >= 3:
        update_training_flag(id=id, niche=niche)
        print(f"The website {url} is offering training based on distinct keyword presence.")
        return True  # Indicating that training was found

    return False  # No sufficient distinct keywords found


# keywords_to_search = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

keywords_to_search = [
    "training", "courses", "workshop", "seminar", "class",
    "certification", "program", "professional development",
    "e-learning", "online courses", "bootcamp", "skill development",
    "learning platform", "virtual learning", "education", "enrollment","event","learn","classes","course"
]

if __name__ == "__main__":
    remaining_websites_count = get_remaining_websites_counts(niche)
    
    while remaining_websites_count > 0:
        # Check if the current website is accessible
        if not check_website(url, id):
            print(f"Website {url} is not accessible. Skipping to the next website...")
            update_website_error_flag(id=id, niche=niche)
            update_training_check_done_flag(id=id, niche=niche)
            # Update website error flag and fetch the next website, don't exit the loop
            data = get_website_from_db(niche)
            url = data[0][1]
            id = data[0][0]
            remaining_websites_count = get_remaining_websites_counts(niche)
            continue  # Skip to the next iteration
        
        # Process the current website if it's accessible
        result = crawl_and_search(url, keywords_to_search)
        update_training_check_done_flag(id=id, niche=niche)
        
        # Fetch the next website data
        data = get_website_from_db(niche)
        url = data[0][1]
        id = data[0][0]
        remaining_websites_count = get_remaining_websites_counts(niche)
