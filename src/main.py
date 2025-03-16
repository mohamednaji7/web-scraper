from bs4 import BeautifulSoup
import time
import html2text
import random
import json
from urllib.parse import urlparse
import os
from rich.console import Console
from rich.logging import RichHandler
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from rich.traceback import install
install()


console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)

logger = logging.getLogger("rich")

class WebClient:



    def get_rendered_soup_response(self, url):
        """get rendered HTML response of an URL"""

        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        page_source = driver.page_source  # Get rendered HTML
        driver.quit()

        soup = BeautifulSoup(page_source, "html.parser")

        return soup


class HtmlCleaner:

        

    def clean_content(self, soup):
        """Clean extracted content"""
    
        # Remove unwanted elements (ads, images, etc.)
        for element in soup.find_all(['script', 'style', 'img', 'svg', 'noscript', 'header', 'footer', 'nav']):
            element.decompose()
            
        # Remove elements with common ad-related class names or ids
        ad_patterns = ['ad', 'ads', 'advertisement', 'banner', 'popup', 'modal', 'cookie']
        # for pattern in ad_patterns:
        #     for element in soup.find_all(class_=re.compile(pattern, re.IGNORECASE)):
        #         element.decompose()
        #     for element in soup.find_all(id=re.compile(pattern, re.IGNORECASE)):
        #         element.decompose()

        # the regex removed everything

        for element in soup.find_all(ad_patterns):
            element.decompose()

        return soup
        
    def get_meta_data(self, soup):
        """Extract meta data"""
        # Extract metadata
        title = soup.title.text.strip() if soup.title else "No Title"        
        
        # Try to get a description from meta tags
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            description = meta_desc['content']
        
        return title, description
    def extract_main_content(self, soup):
        """Extracts main content from a webpage and converts it into Markdown"""
        
        # Find the main content container
        main_container = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not main_container:
            print(soup.prettify())
            raise Exception("Could not find main content container or body")

        # Convert HTML to Markdown
        markdown_converter = html2text.HTML2Text()
        markdown_converter.ignore_links = False  # Set to True if you don't want links
        markdown_content = markdown_converter.handle(str(main_container))

        return markdown_content
    



    def extract_content(self, soup):
        """Extract relevant content from a URL"""

        # Clean content
        soup = self.clean_content(soup)


        # Extract meta data
        title, description = self.get_meta_data(soup) 


        # Extract main content
        main_content = self.extract_main_content(soup)   

        
        return {
            'title': title,
            'description': description,
            'content_length': len(main_content),
            'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'main_content': main_content,
        }
            

import matplotlib.pyplot as plt

class WebScraper:
    def __init__(self, delay, processing_time, number_of_urls_to_scrape, output_dir="scraped_data"):
        self.web_client = WebClient()
        self.html_cleaner = HtmlCleaner()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.processing_time = processing_time
        self.delay = delay
        self.number_of_urls_to_scrape = number_of_urls_to_scrape
        self.total_number_of_urls_to_scrape = number_of_urls_to_scrape
        
    def extract_domain(self, url):
        parsed_uri = urlparse(url)
        return parsed_uri.netloc

    def scrape_urls(self, urls, scraping_states, subdir):
        """Scrape a list of URLs with a delay between requests"""
        if subdir:
            output_dir = f"{self.output_dir}/{subdir}"
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = self.output_dir
        results = []
        # for url in urls:
        new_scraping_states = []
        info = []
        for url, state in zip(urls, scraping_states):
            if state == True:
                logger.info(f"Skipping...")
                new_scraping_states.append(True)
                info.append("scraped")

                continue
            

            logger.info(f"Scraping: {url}")
            logger.info(f"reaminig time: {self.processing_time*self.number_of_urls_to_scrape/60:.2f} minutes")
            print(self.number_of_urls_to_scrape)
            print(self.total_number_of_urls_to_scrape)
            logger.info(f"url {-self.number_of_urls_to_scrape+self.total_number_of_urls_to_scrape}/{self.total_number_of_urls_to_scrape}")
            self.number_of_urls_to_scrape -= 1
            start_time = time.time()
            try:
                # Be respectful with a delay between requests
                time.sleep(self.delay)

                # soup = self.web_client.get_soup_response(url)
                soup = self.web_client.get_rendered_soup_response(url)
                soup = self.html_cleaner.clean_content(soup)
                                
                                

                data = self.html_cleaner.extract_content(soup)       
                # Save individual result as text file
                if data['main_content']:
                    # Add data to results
                    results.append(data)
                    domain = self.extract_domain(url)
                    filename = f"{output_dir}/{domain} - {data['title']}.txt"

                    # Check if the filename makes an error in writing then change the file name
                    try:   
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write("Writing is working")
                    except:
                        filename = f"{output_dir}/{domain} - {data['scrape_timestamp']}.txt"

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"URL: {url}\n")
                        # add the sraping time to the file
                        f.write(f"SCRAPING TIME: {data['scrape_timestamp']}\n")
                        f.write(f"TITLE: {data['title']}\n")
                        f.write(f"DESCRIPTION: {data['description']}\n")
                        f.write(f"\n")
                        f.write(data['main_content'])
                            
                    with open(filename.replace('.txt', '.md'), 'w', encoding='utf-8') as f:
                        f.write(data['main_content'])
                
                new_scraping_states.append(True)
                info.append("scraped")

                
            except Exception as e:
                logger.error(f"{e}")
                console.print_exception()
                new_scraping_states.append(False)
                info.append(f"{e}")

            
            # update the  processing time to averging 
            processing_time = time.time() - start_time
            self.processing_time = (self.processing_time + processing_time) / 2


        # Save to a JSON file with indentation  do not overwrite the json results if it exist 
        json_path = f"{output_dir}/scraped_data.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.extend(data)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Scraping completed. Data saved to {json_path}")


        return new_scraping_states, info
     

def main():
    main_dir = "output/scraped_data"
    os.makedirs(main_dir, exist_ok=True)
    
    urls_JSON = json.load(open('input/urls.json'))
    summary = {}
    total_number_of_urls = sum([
        len(urls_JSON[key]['scraping_states']) - sum(urls_JSON[key]['scraping_states']) 
            for key in urls_JSON
        ])
    start_time = time.time()
    delay = 2
    scraper = WebScraper(delay, delay, total_number_of_urls, main_dir)
    for key in urls_JSON:
        urls_to_scrape = urls_JSON[key]['links']
        scraping_states = urls_JSON[key]['scraping_states']
        
        new_scraping_states , info = scraper.scrape_urls(urls_to_scrape, scraping_states, key)


        urls_JSON[key]['scraping_states'] = new_scraping_states

        # only add info if there at leas one falid scrape (not 'scraped')
        if sum(new_scraping_states) < len(new_scraping_states):
            urls_JSON[key]['info'] = info
        else:
            # drop the info if it exist 
            if 'info' in urls_JSON[key]:
                del urls_JSON[key]['info']
        
        summary[key] = {
            "total_links": len(urls_to_scrape),
            "scraped": sum(new_scraping_states),
            "failed": len(urls_to_scrape) - sum(new_scraping_states),
        }
        
        
    # Save to a JSON file with indentation
    with open("input/urls.json", "w", encoding="utf-8") as f:
        json.dump(urls_JSON, f, indent=4, ensure_ascii=False)  # ensure_ascii=False keeps Unicode characters
        
    
        # print  time.time() - start_time
    logger.info(f"Total number of links: {total_number_of_urls}")
    logger.info(f"Total time: {(time.time() - start_time)/60:.2f}m")
    json_summary_path = f"{main_dir}/summary.json"
    with open(json_summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Summary saved to {json_summary_path}")
    
    
    # Plot results
    keys = list(summary.keys())
    scraped = [summary[k]['scraped'] for k in keys]
    failed = [summary[k]['failed'] for k in keys]
    
    plt.figure(figsize=(10, 5))
    plt.bar(keys, scraped, color='green', label='Scraped')
    plt.bar(keys, failed, color='red', bottom=scraped, label='Failed')
    plt.xlabel("Categories")
    plt.ylabel("Number of Links")
    plt.title("Scraping Results")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_path = f"{main_dir}/scraping_results.png"
    plt.savefig(plot_path)
    logger.info(f"Plot saved to {plot_path}")

if __name__ == "__main__":
    main()
