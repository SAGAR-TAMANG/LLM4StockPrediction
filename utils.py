from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import openai

def fetch_news(query, experiment):
    """
    # Fetch News
    - Selenium
    - Webdriver
    """
    
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
    print(df.head())
    
    # df.to_excel("infosys_news_results.xlsx", index=False)
    # print("Saved data to infosys_news_results.xlsx")
    
    json_str = df.to_json(orient='records')

    with open(f"data/{query}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{experiment}.json", "w") as f:
        f.write(json_str)

    return json_str

def create_prompt_1(query, news):
    """
    # Create Prompt 1
    - Zero shot prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price not given
    
    query: Company Name
    news: News related to the Company
    """
    prompt = f"""I will give you latest 10 news related to the company: {query}

News:
{news}


Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:

{{
    "company_name": "Company Name",
    "rating": "Your predicted score among: -2, -1, 0, 1, 2 where -2 is Strong Sell, -1 is Moderate Sell, 0 is Hold, 1 is Moderate Buy, and 2 is Strong Buy."
}}"""
    
    return prompt

def create_prompt_2(last_price, query, news):
    """
    # Create Prompt 2
    - Zero shot prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price is given
    
    query: Company Name
    news: News related to the Company
    """
    prompt = f"""I will give you latest 10 news related to the company: {query}. The last price of {query} was {last_price}.
    
    News:
    {news}
    
    
    Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:
    
    {{
        "company_name": "Company Name",
        "performance_at_closing_tomorrow": "Your predicted performance of the stock in percentage increase/decrease (Example: -0.5% or +1.2%)"
    }}
    """
    
    return prompt

def create_prompt_3(last_price, query, news):
    """
    # Create Prompt 3
    - Few shot prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price is given
    
    query: Company Name
    news: News related to the Company
    """
    prompt_1 = f"""I will give you latest 10 news related to the company: {query}. The last price of {query} was {last_price}.
    
    News:
    {news}
    """
    
    prompt_2 = f"""Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:
    
    {{
        "company_name": "Company Name",
        "performance_at_closing_tomorrow": "Your predicted performance of the stock in percentage increase/decrease (Example: -0.5% or +1.2%)"
    }}
    """
    
    return prompt_1, prompt_2

def create_prompt_4(last_price, query, news):
    """
    # Create Prompt 4
    - Few shot prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price is given
    
    query: Company Name
    news: News related to the Company
    """
    prompt_1 = f"""I will give you latest 10 news related to the company: {query}. The last price of {query} was {last_price}.
    """
    
    prompt_2 = f"""News:
    {news}"""
    
    prompt_3 = f"""Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:
    
    {{
        "company_name": "Company Name",
        "performance_at_closing_tomorrow": "Your predicted performance of the stock in percentage increase/decrease (Example: -0.5% or +1.2%)"
    }}
    """
    
    return prompt_1, prompt_2, prompt_3

def create_prompt_5(last_price, query, news):
    """
    # Create Prompt 5
    - Chain-of-Thought (CoT) prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price is given
    
    query: Company Name
    news: News related to the Company
    """
    prompt_1 = f"""I will give you latest 10 news related to the company: {query}. The last price of {query} was {last_price}.
    
    News:
    {news}
    
    
    Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:
    
    {{
        "company_name": "Company Name",
        "performance_at_closing_tomorrow": "Your predicted performance of the stock in percentage increase/decrease (Example: -0.5% or +1.2%)"
    }}
    
    **IMPORTANT**: You will think out loud. I.e., You will be following the Chain-of-Thought prompting technique. You will think about it in a chain making your thoughts visible.
    """
    
    return prompt_1

def create_prompt_6(last_price, query, news):
    """
    # Create Prompt 6
    - Chain-of-Thought (CoT) prompting
    - Simple JSON Response
    - Normal text input format
    - No persona given
    - Company's previous performance not given
    - Company's present last price is given
    
    query: Company Name
    news: News related to the Company
    """
    prompt_1 = f"""I will give you latest 10 news related to the company: {query}. The last price of {query} was {last_price}.
    
    News:
    {news}
    
    
    Now, based on these news you will give a prediction of how this company's stock market will perform tomorrow. Give the response in this JSON format:
    
    {{
        "company_name": "Company Name",
        "performance_at_closing_tomorrow": "Your predicted performance of the stock in percentage increase/decrease (Example: -0.5% or +1.2%)"
    }}
    
    **IMPORTANT**: You will think out loud. I.e., You will be following the Chain-of-Thought prompting technique. You will think about it in a chain making your thoughts visible.
    """
    
    return prompt_1


client = openai.OpenAI()

def get_openai_response(prompt: str, model: str = "gpt-4o") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            response_format={"type": "json_object"},
        )

        response = response.choices[0].message.content
        
        # 1. Remove the starting fence
        if response.startswith("```json"):
            response = response[len("```json"):]

        # 2. Remove the ending fence
        if response.endswith("```"):
            response = response[:-len("```")]

        # Strip any extra whitespace
        response = response.strip()
        
        return response
    except Exception as e:
        return f"Error: {e}"
