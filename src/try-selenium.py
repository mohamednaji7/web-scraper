from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url ="https://smertevidenskab.dk/viden-om-smerter/artikler/piskesmaeld-haab-om-smertefrihed/?_gl=1*1mdoimu*_up*MQ..*_gs*MQ..&gclid=CjwKCAjwvr--BhB5EiwAd5YbXqJjhTF_GheLfRfgfEEdW0kMlxGKQqS2dpInP5L6TZN10QAT3eAcZhoCyqYQAvD_BwE"

driver.get(url)

page_source = driver.page_source  # Get rendered HTML
driver.quit()

soup = BeautifulSoup(page_source, "html.parser")


main_container = soup.find('main') or soup.find('article') or soup.find('body')
if not main_container:
    print(soup.prettify())

    raise Exception("Could not find main content container or body")

# print(main_container.prettify())
# print('*'*100)
print(main_container.text)
print('*'*100)
print('main_container not None')
