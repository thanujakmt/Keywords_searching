
import requests
from bs4 import BeautifulSoup
from collections import Counter

# Function to extract all internal links
def get_internal_links(base_url, soup):
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/') or base_url in href:
            full_url = href if href.startswith('http') else base_url + href
            if full_url not in links:
                links.append(full_url)
    return links

# Function to count keywords on a page
def count_keywords(url, keywords):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text().lower()
    word_count = Counter(text.split())
    return {keyword: word_count[keyword] for keyword in keywords}

# Base URL
base_url = 'http://www.apothecarysuilcrow.com/'

# Fetch the homepage and find internal links
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')
internal_links = get_internal_links(base_url, soup)

# Keywords to search for
keywords = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']
    
# Count keywords on each page
total_counts = Counter()
for link in internal_links:
    keyword_counts = count_keywords(link, keywords)
    print(f"Counts for {link}: {keyword_counts}")
    total_counts.update(keyword_counts)

print(f"Total keyword counts across all pages: {total_counts}")


# import requests
# from bs4 import BeautifulSoup
# from collections import Counter
# import pandas as pd

# # Function to extract all internal links
# def get_internal_links(base_url, soup):
#     links = []
#     for a_tag in soup.find_all('a', href=True):
#         href = a_tag['href']
#         if href.startswith('/') or base_url in href:
#             full_url = href if href.startswith('http') else base_url + href
#             if full_url not in links:
#                 links.append(full_url)
#     return links

# # Function to count keywords on a page
# def count_keywords(url, keywords):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     text = soup.get_text().lower()
#     word_count = Counter(text.split())
#     return {keyword: word_count[keyword] for keyword in keywords}

# # List of URLs to check
# urls = [
#     "http://www.apothecarysuilcrow.com/",
#     "https://www.sageandstoneapothecaryinc.com/",
#     "http://aromaleeshop.com/",
#     "http://www.biotone.com/",
#     "http://wildwillowholistics.com/",
#     "https://chthonicstar.com/",
#     "https://leydenhouse.com/",
#     "http://wellnessawaits.org/",
#     "https://www.serenitywellnesscny.com/",
#     "https://peacefilsagemassage.abmp.com/",
#     "https://www.gnomelicious.com/",
#     "http://soapsandsuchalpena.com/",
#     "http://www.apassionforlife.ca/",
#     "http://meltcandleshop.com/",
#     "http://www.pureherbs.com/",
#     "http://www.shopelementoonline.com/",
#     "https://www.nationalnutrition.ca/",
#     "https://nesthamilton.com/",
#     "https://www.sweetfiretobacco.com/",
#     "http://www.thisismade.ca/",
#     "http://www.blackbirdsdaughter.com/",
#     "http://www.cottonborofarm.com/",
#     "https://www.kriyatouch.com/",
#     "https://aromajam.bigcartel.com/",
#     "http://www.gentlebalancemassage.com/",
#     "http://www.sonjasecrets.com/",
#     "http://www.preciousessentials4u.com/",
#     "http://www.zenfulflamescandles.com/",
#     "http://www.pillarsofthrow.com/",
#     "http://melissasbotanicals.com/",
#     "http://herbalalchemyshop.biz/",
#     "http://www.sweetmana.com/",
#     "http://www.dharmaobjects.com/",
#     "http://www.ladyandthebeard.com/",
#     "http://ninekeysapothecary.com/",
#     "http://www.theoasismassage.com/",
#     "https://www.purelyrelaxation.com/",
#     "https://www.ultimateintegrativehealth.com/"
# ]

# # Keywords to search for
# keywords = ['course', 'courses', 'training', 'event', 'seminar', 'workshop', 'class', 'classes']

# # Loop through each URL
# for base_url in urls:
#     total_counts = Counter()
#     link_counts = {}  # Initialize link_counts outside the try block
#     try:
#         # Fetch the homepage and find internal links
#         response = requests.get(base_url)
#         soup = BeautifulSoup(response.content, 'html.parser')
#         internal_links = get_internal_links(base_url, soup)

#         # Count keywords on the homepage
#         homepage_counts = count_keywords(base_url, keywords)
#         total_counts.update(homepage_counts)

#         # Count keywords on each internal link
#         for link in internal_links:
#             keyword_counts = count_keywords(link, keywords)
#             link_counts[link] = keyword_counts
#             total_counts.update(keyword_counts)

#         # Check if link_counts has any data before creating DataFrame
#         if link_counts or homepage_counts:
#             df = pd.DataFrame.from_dict(link_counts, orient='index').fillna(0)
#             df.loc['Homepage'] = homepage_counts  # Add homepage counts as last row

#             # Save to Excel
#             excel_filename = f"{base_url.split('//')[1].replace('/', '_')}_keyword_counts.xlsx"
#             df.to_excel(excel_filename, index=True, sheet_name='Keyword Counts')

#             print(f"Keyword counts saved for {base_url} to {excel_filename}")
#         else:
#             print(f"No keyword counts found for {base_url}")

#     except Exception as e:
#         print(f"Error processing {base_url}: {e}")

# # Final message
# print("Processing complete.")

