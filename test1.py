# # import requests
# # from bs4 import BeautifulSoup
# # import pandas as pd
# # from urllib.parse import urljoin, urlparse

# # # List of keywords to search for
# # keywords = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

# # # List of URLs to search
# # urls = [
# #     "http://www.apothecarysuilcrow.com/",
# #     "https://www.sageandstoneapothecaryinc.com/"
# # ]

# # # Function to check for keywords in the website text
# # def check_keywords(text):
# #     return {keyword: (1 if keyword in text else 0) for keyword in keywords}

# # # Function to fetch all internal links from a URL
# # def get_internal_links(base_url):
# #     internal_links = set()
# #     try:
# #         response = requests.get(base_url)
# #         response.raise_for_status()
# #         soup = BeautifulSoup(response.text, 'html.parser')
        
# #         for link in soup.find_all('a', href=True):
# #             href = link['href']
# #             # Create absolute URL and check if it's internal
# #             absolute_url = urljoin(base_url, href)
# #             if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
# #                 internal_links.add(absolute_url)
# #     except requests.RequestException as e:
# #         print(f"Error fetching internal links from {base_url}: {e}")
    
# #     return internal_links

# # # Iterate over each URL and collect results
# # for url in urls:
# #     internal_links = get_internal_links(url)
# #     keyword_results = {}
    
# #     for link in internal_links:
# #         try:
# #             response = requests.get(link)
# #             response.raise_for_status()
# #             text = response.text.lower()  # Get text content and convert to lowercase
# #             keyword_results[link] = check_keywords(text)
# #         except requests.RequestException as e:
# #             print(f"Error fetching {link}: {e}")
# #             keyword_results[link] = {keyword: 0 for keyword in keywords}  # Assume no keywords if there's an error
    
# #     # Create DataFrame
# #     df = pd.DataFrame(keyword_results).T  # Transpose to have links as rows
# #     df.index.name = 'Internal Links'
    
# #     # Save to Excel file named after the base URL
# #     base_url_name = urlparse(url).netloc.replace('.', '_')
# #     df.to_excel(f'{base_url_name}_keyword_results.xlsx')

# #     print(f"Results saved to {base_url_name}_keyword_results.xlsx")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse

# List of keywords to search for
keywords = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

# List of URLs to search
urls = [
   "http://www.apothecarysuilcrow.com/",
    "https://www.sageandstoneapothecaryinc.com/",
    "http://aromaleeshop.com/",
    "http://www.biotone.com/",
    "http://wildwillowholistics.com/",
    "https://chthonicstar.com/",
    "https://leydenhouse.com/",
    "http://wellnessawaits.org/",
    "https://www.serenitywellnesscny.com/",
    "https://peacefilsagemassage.abmp.com/"
]

# Function to check for keywords in the website text
def check_keywords(text):
    return {keyword: (1 if keyword in text else 0) for keyword in keywords}

# Function to fetch all internal links from a URL
def get_internal_links(base_url):
    internal_links = set()
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Create absolute URL and check if it's internal
            absolute_url = urljoin(base_url, href)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                internal_links.add(absolute_url)
    except requests.RequestException as e:
        print(f"Error fetching internal links from {base_url}: {e}")
    
    return internal_links

# Iterate over each URL and collect results
final_results = []

for url in urls:
    internal_links = get_internal_links(url)
    keyword_results = {}
    
    for link in internal_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            text = response.text.lower()  # Get text content and convert to lowercase
            keyword_results[link] = check_keywords(text)
        except requests.RequestException as e:
            print(f"Error fetching {link}: {e}")
            keyword_results[link] = {keyword: 0 for keyword in keywords}  # Assume no keywords if there's an error
    
    # Create DataFrame
    df = pd.DataFrame(keyword_results).T  # Transpose to have links as rows
    df.index.name = 'Internal Links'
    
    # Save to Excel file named after the base URL
    base_url_name = urlparse(url).netloc.replace('.', '_')
    df.to_excel(f'{base_url_name}_keyword_results.xlsx')

    # Add the summary result for the website
    overall_status = any(any(count for count in link_info.values()) for link_info in keyword_results.values())
    final_results.append({'Website': base_url_name, 'Status': overall_status})

    print(f"Results saved to {base_url_name}_keyword_results.xlsx")

# Create final summary DataFrame
final_df = pd.DataFrame(final_results)
final_df.to_excel('final_keyword_summary.xlsx', index=False)

print("Final summary saved to final_keyword_summary.xlsx")
