"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""
import os
import sys
import json
from datetime import datetime
import requests
import bs4
import loguru

def scrape_data_point():
    """
    Scrapes the top headline from the 'News' section on The Daily Pennsylvanian home page by first navigating to the 'News' subpage and then extracting the headline.
    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        news_link = soup.find("a", href=lambda x: x and "section/news" in x)
        if news_link:
            news_page = requests.get(news_link['href'])
            loguru.logger.info(f"News page URL: {news_page.url}")
            if news_page.ok:
                news_soup = bs4.BeautifulSoup(news_page.text, "html.parser")
                main_section = news_soup.find("div", class_="main section")
                if main_section:
                    top_headline = main_section.find("h3", class_="standard-link")
                    if top_headline and top_headline.find("a"):
                        top_headline_text = top_headline.find("a").text.strip()
                        loguru.logger.info(f"Top headline: {top_headline_text}")
                        return top_headline_text
    loguru.logger.info("Failed to locate the News link or headline")
    return None

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                loguru.logger.error("Error decoding JSON from file")
                return {}
    return {}

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    loguru.logger.add("scrape.log", rotation="1 day")
    data_file_path = 'data/daily_pennsylvanian_headlines.json'
    current_data = load_data(data_file_path)

    today_date = datetime.now().strftime("%Y-%m-%d")
    data_point = scrape_data_point()

    if data_point:
        if today_date in current_data:
            current_data[today_date].append(data_point)
        else:
            current_data[today_date] = [data_point]

        save_data(data_file_path, current_data)
        loguru.logger.info(f"Scraped and saved: {data_point}")
    else:
        loguru.logger.info("No new data to save.")

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
        loguru.logger.info("Created data directory")

    main()
    
    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")

