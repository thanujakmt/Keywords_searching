 
# import requests
# from bs4 import BeautifulSoup
# import re
# from database_handler import *
# from config import *
# import time
# import retry

# data = get_website_from_db(niche)
# url = data[0][1]
# gl_id = data[0][0]

# def check_website(url):
#     try:
#         response = requests.get(url)
#         time.sleep(5)
#         if response.status_code == 200:
#             print(f"Website {url} is accessible.")
#             return True
#         else:
#             print(f"Website {url} returned status code {response.status_code}.")
#             return False
#     except requests.exceptions.RequestException as e:
#         print(f"Website {url} is not accessible. Error: {e}")
#         return False

# # List of file extensions to exclude
# EXCLUDED_EXTENSIONS = [".pdf", ".jpg", ".zip", ".mp4", ".webp", ".webm", 
#                        ".json", ".xml", ".csv", ".xlsx", ".doc", ".docx", 
#                        ".jpeg", ".png", ".ico", ".css"]

# def get_internal_links(url, domain):
#     # First, check if the website is accessible
#     if not check_website(url):
#         print("Website not accessible. Marking it as such after retries.")
#         # Update the website error flag in the database
#         update_website_error_flag(gl_id=gl_id, niche=niche)
#         return "Website not accessible."

#     retries = 0
#     while retries < 3:
#         try:
#             # Attempt to fetch the website content
#             response = requests.get(url)
#             response.raise_for_status()
#             soup = BeautifulSoup(response.text, 'html.parser')

#             links = set()
#             for a_tag in soup.find_all('a', href=True):
#                 href = a_tag['href']
#                 # Ensure it is an internal link (relative or with the same domain)
#                 if href.startswith('/') or domain in href:
#                     full_url = requests.compat.urljoin(url, href)  
#                     # Exclude URLs with the listed file extensions
#                     if not any(full_url.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
#                         links.add(full_url)

#             # If links are found, return them
#             print(f"Found internal links: {links}")
#             return links
        
#         except requests.exceptions.RequestException as e:
#             retries += 1
#             print(f"Error fetching links (attempt {retries}/{3}): {str(e)}")
#             if retries < 3:
#                 print(f"Retrying in {5} seconds...")
#                 time.sleep(5)  # Wait before retrying

#     # If we exhaust the retries, return an error and log it
#     print(f"Max retries reached. Unable to access website {url}")
#     update_website_error_flag(gl_id=gl_id, niche=niche)
#     return "Website not accessible after retries."

# def search_keywords_in_page(url, keywords):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()

#         # Use BeautifulSoup to parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Extract only the visible text from the page
#         page_text = soup.get_text(separator=' ')  # Using a space separator between elements

#         found_keywords = {}
#         for keyword in keywords:
#             # Search for the keyword in the page text (not HTML tags)
#             if re.search(rf"\b{keyword}\b", page_text, re.IGNORECASE):
#                 found_keywords[keyword] = 1
#             else:
#                 found_keywords[keyword] = 0

#         return found_keywords
#     except Exception as e:
#         print(f"Error fetching page {url}: {str(e)}")
#         return {}

# def crawl_and_search(url, keywords):
#     domain = requests.compat.urlparse(url).netloc
#     internal_links = get_internal_links(url, domain)

#     # Check if internal_links is None or a string indicating an error
#     if not internal_links or isinstance(internal_links, str):
#         print(f"Error retrieving internal links: {internal_links}")
#         return False  # Return False to indicate no keywords found

#     training_found = False
#     results = {}  # Dictionary to hold link status results

#     for link in internal_links:
#         keyword_results = search_keywords_in_page(link, keywords)
#         results[link] = keyword_results  # Store keyword results for each link

#         if any(keyword_results.values()):  # Check if any keyword was found
#             training_found = True  # Set this to True if any keywords are found

#     # Print the status of keyword presence for each link
#     for link, keyword_status in results.items():
#         print(f"{link}: {keyword_status}")

#     # Update flags based on whether training keywords were found
#     if training_found:
#         update_training_flag(gl_id=gl_id, niche=niche)
#         print(f"The website {url} is offering training based on keyword presence.")

#     return training_found  # Return whether training was found

# keywords_to_search = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

# if __name__ == "__main__":

#     remaining_websites_count = get_remaining_websites_counts(niche)
#     while remaining_websites_count > 0:
#         result = crawl_and_search(url, keywords_to_search)
#         update_training_check_done_flag(gl_id=gl_id, niche=niche)  # Update once per website
#         remaining_websites_count = get_remaining_websites_counts(niche)
#         if remaining_websites_count > 0:
#             # Get the next website if available
#             data = get_website_from_db(niche)
#             url = data[0][1]
#             gl_id = data[0][0] 

import requests
from bs4 import BeautifulSoup
import re
from database_handler import *
from config import *
import time
import retry
import multiprocessing
from fake_useragent import UserAgent

# Use fake user agent for random headers
ua = UserAgent()

data = get_website_from_db(niche)
url = data[0][1]
gl_id = data[0][0]

# Headers to avoid being blocked
def get_headers():
    return {'User-Agent': ua.random}

def check_website(url):
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers)
        time.sleep(5)
        if response.status_code == 200:
            print(f"Website {url} is accessible.")
            return True
        else:
            print(f"Website {url} returned status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Website {url} is not accessible. Error: {e}")
        return False

# List of file extensions to exclude
EXCLUDED_EXTENSIONS = [".pdf", ".jpg", ".zip", ".mp4", ".webp", ".webm", 
                       ".json", ".xml", ".csv", ".xlsx", ".doc", ".docx", 
                       ".jpeg", ".png", ".ico", ".css"]
def get_internal_links(url, domain):
    # First, check if the website is accessible
    if not check_website(url):
        print("Website not accessible. Marking it as such after retries.")
        update_website_error_flag(gl_id=gl_id, niche=niche)
        return "Website not accessible."

    retries = 0
    while retries < 3:
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
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
    update_website_error_flag(gl_id=gl_id, niche=niche)
    return "Website not accessible after retries."

def search_keywords_in_page(url, keywords):
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ')

        found_keywords = {}
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", page_text, re.IGNORECASE):
                found_keywords[keyword] = 1
            else:
                found_keywords[keyword] = 0

        return found_keywords
    except Exception as e:
        print(f"Error fetching page {url}: {str(e)}")
        return {}

def crawl_and_search(url, keywords):
    domain = requests.compat.urlparse(url).netloc
    internal_links = get_internal_links(url, domain)

    if not internal_links or isinstance(internal_links, str):
        print(f"Error retrieving internal links: {internal_links}")
        return False

    training_found = False
    results = {}

    def process_link(link):
        nonlocal training_found
        keyword_results = search_keywords_in_page(link, keywords)
        results[link] = keyword_results
        if any(keyword_results.values()):
            training_found = True

    with multiprocessing.Pool() as pool:
        pool.map(process_link, internal_links)

    for link, keyword_status in results.items():
        print(f"{link}: {keyword_status}")

    if training_found:
        update_training_flag(gl_id=gl_id, niche=niche)
        print(f"The website {url} is offering training based on keyword presence.")

    return training_found

keywords_to_search = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

if __name__ == "__main__":
    remaining_websites_count = get_remaining_websites_counts(niche)
    while remaining_websites_count > 0:
        result = crawl_and_search(url, keywords_to_search)
        update_training_check_done_flag(gl_id=gl_id, niche=niche)
        remaining_websites_count = get_remaining_websites_counts(niche)
        if remaining_websites_count > 0:
            data = get_website_from_db(niche)
            url = data[0][1]
            gl_id = data[0][0]
