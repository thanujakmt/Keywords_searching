
import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
from multiprocessing import Pool, cpu_count
from database_handler import get_website_from_db

# List of keywords to search for
keywords = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

urls = get_website_from_db()

# Create a folder to store all the Excel files
output_folder = 'keyword_results_folder'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

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

# Function to handle 429 errors with retries and backoff
def fetch_with_retry(url, retries=5):
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 429:
                # Check for the Retry-After header and wait accordingly
                retry_after = int(response.headers.get("Retry-After", 2))  # Default to 2 seconds if not present
                print(f"429 Error for {url}. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue  # Retry the request after sleeping
            response.raise_for_status()
            return response.text.lower()  # Return the response text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    return None

# Function to process each URL in parallel
def process_url(url):
    internal_links = get_internal_links(url)
    keyword_results = {}
    
    for link in internal_links:
        text = fetch_with_retry(link)
        if text:
            keyword_results[link] = check_keywords(text)
        else:
            keyword_results[link] = {keyword: 0 for keyword in keywords}

    # Create DataFrame for each website
    df = pd.DataFrame(keyword_results).T  # Transpose to have links as rows
    df.index.name = 'Internal Links'
    
    # Save to Excel file inside the output folder
    base_url_name = urlparse(url).netloc.replace('.', '_')
    file_path = os.path.join(output_folder, f'{base_url_name}_keyword_results.xlsx')
    df.to_excel(file_path)

    # Add the summary result for the website
    overall_status = any(any(count for count in link_info.values()) for link_info in keyword_results.values())
    return {'Website': url, 'Status': overall_status}

# Main function to handle multiprocessing
def main():
    # Use all available CPUs
    pool_size = cpu_count()

    with Pool(pool_size) as pool:
        # Distribute URLs across processes
        final_results = pool.map(process_url, urls)

    # Create final summary DataFrame
    final_df = pd.DataFrame(final_results)
    final_summary_path = os.path.join(output_folder, 'final_keyword_summary.xlsx')
    final_df.to_excel(final_summary_path, index=False)

    print(f"Final summary saved to {final_summary_path}")

def delete_unwanted_excel_files(output_folder, summary_file):
    for file_name in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file_name)
        if file_name != summary_file and file_name.endswith('.xlsx'):
            os.remove(file_path)
            print(f"Deleted: {file_path}")

if __name__ == '__main__':
    main()
    summary_file = 'final_keyword_summary.xlsx'
    delete_unwanted_excel_files(output_folder, summary_file)
