
import nest_asyncio
nest_asyncio.apply()
from pysitemap import crawler
from pysitemap.parsers.lxml_parser import Parser
import xml.etree.ElementTree as ET
import os
import requests
from bs4 import BeautifulSoup
import re
import multiprocessing
import pandas as pd

def save_to_excel(data, url):
    
    filename = url.replace('/','').replace('https','').replace('http','').replace(":",'').replace(".","_")
    filename = f"{filename}.xlsx"
    print(filename)

    rows = []
    for entry in data:
        url, metrics = list(entry.items())[0]
        rows.append({'URL': url, 'Admin': metrics['Admin'], 'helenzys': metrics['helenzys']})

    # Create DataFrame
    df = pd.DataFrame(rows)

    output_dir = os.path.join(os.getcwd(),'output')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Save to Excel
    df.to_excel(os.path.join(output_dir,filename), index=False)
    print(f"Data saved to {filename}")

def read_urls_from_xml(file_path):
    # Parse the XML file containing the sitemap
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Define the XML namespace for sitemap parsing
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    # Extract URLs from <loc> elements within <url> tags
    urls = [url.find('ns:loc', namespace).text for url in root.findall('ns:url', namespace)]
    
    return urls

def get_all_sub_domains(domain):
    # Define the path for the sitemap file
    sitemap_path = os.path.join(os.getcwd(), 'sitemap', 'sitemap.xml')
    
    # Remove existing sitemap if it exists
    if os.path.exists(sitemap_path):
        os.remove(sitemap_path)
    
    # Create the sitemap directory if it doesn't exist
    os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)

    # Crawl the specified domain and save the sitemap
    crawler(
        domain, out_file=sitemap_path, 
        exclude_urls=[".pdf", ".jpg", ".zip", ".mp4", ".webp", ".webm", 
                      ".json", ".xml", ".csv", ".xlsx", ".doc", ".docx", 
                      ".jpeg", ".png", ".ico",".css"],  # Exclude certain file types
        http_request_options={"ssl": False}, parser=Parser
    )

    # Read URLs from the generated sitemap
    urls = read_urls_from_xml(sitemap_path)
    
    # Remove the sitemap file after extraction
    os.remove(sitemap_path)
    return urls

def count_keywords(text, keywords):
    print("Counting...")
    count_dict = {}
    text = text.lower()  # Convert text to lowercase for uniformity
    
    # Check if keywords is a list or a single keyword
    if isinstance(keywords, list):
        for keyword in keywords:
            count_dict[keyword] = text.count(keyword.lower())  # Count occurrences of each keyword
    else:
        count_dict[keywords] = text.count(keywords.lower())  # Count single keyword
    
    return count_dict

def get_keyword_count_in_each_url(args):
    url, keywords = args
    print(f"Fetching Text: {url}")
    
    try:
        response = requests.get(url, timeout=15)  # Fetch URL with a timeout
    except requests.exceptions.RequestException:
        return {url: "Error fetching url"}  # Return error message if fetching fails
    
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        response_body_text = soup.get_text()  # Get the text content
        response_body_text = re.sub(r'\s+', ' ', response_body_text).strip()  # Clean up whitespace
        return {url: count_keywords(response_body_text, keywords)}  # Count keywords in the text
    else:
        return {url: "Error fetching url"}  # Handle non-200 responses

def get_result(urls, keywords):
    # Prepare the URLs for multiprocessing
    urls = [(url, keywords) for url in urls]
    
    # Use multiprocessing to count keywords across multiple URLs
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(get_keyword_count_in_each_url, urls)
    
    return results

def get_resutl(url,keywords,set_urls_limit):
    # Get all subdomains from the specified website
    urls = get_all_sub_domains(url)

    # Limit the number of URLs if a limit is set
    if set_urls_limit > 0:
        urls = urls[:set_urls_limit]
    
    # Get keyword counts for each URL and print results
    result = get_result(urls, keywords)
    save_to_excel(data = result, url = url)
    return result

if __name__ == '__main__':

    
    url_list = [
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

    
    # Define keywords to search for
    keywords = ['Admin','helenzys']
    set_urls_limit = 10  # Set a limit for the number of URLs to process

    for url in url_list:

        result = get_resutl(url,keywords,set_urls_limit)
        print(result)
