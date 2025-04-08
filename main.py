import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def fetch_infosys_news(query):
    # Chrome setup
    CHROMEDRIVER_PATH = r'C:\Users\TAMANG\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe'
    CHROME_BINARY_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_PATH
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Anti-bot: override navigator.webdriver
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {
            'source': """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        }
    )

    # Open news search
    target_url = f"https://www.google.com/search?q={query}&tbm=nws&tbs=sbd:1"
    driver.get(target_url)
    print("Opened:", target_url)
    time.sleep(10)

    # Use BeautifulSoup to parse page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    news_data = []

    search_div = soup.find("div", id="search")
    if search_div:
        news_cards = search_div.find_all("div", class_="SoaBEf")
        print(f"Found {len(news_cards)} news cards.")

        for card in news_cards:
            try:
                # Link
                a_tag = card.find("a", class_="WlydOe")
                link = a_tag['href'] if a_tag else ""

                # Title
                title_div = card.find("div", class_="n0jPhd")
                title = title_div.get_text(strip=True) if title_div else ""

                # Description
                desc_div = card.find("div", class_="GI74Re")
                description = desc_div.get_text(strip=True) if desc_div else ""

                # Source
                source_span = card.find("div", class_="MgUUmf").find("span")
                source = source_span.get_text(strip=True) if source_span else ""

                # Time
                time_div = card.find("div", class_="OSrXXb")
                published_time = time_div.get_text(strip=True) if time_div else ""

                news_data.append({
                    "Title": title,
                    "Description": description,
                    "Source": source,
                    "Published Time": published_time,
                    "Link": link
                })
            except Exception as e:
                print("Error parsing one card:", e)
    else:
        print("Search div not found.")

    # Save to Excel
    df = pd.DataFrame(news_data)
    df.to_excel("infosys_news_results.xlsx", index=False)
    print("Saved data to infosys_news_results.xlsx")