"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys
import json
from datetime import datetime
import loguru
import requests
import bs4

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
                    top_headline_text = top_headline.find("a").text.strip() if top_headline else ""
                    loguru.logger.info(f"Top headline: {top_headline_text}")
                    return top_headline_text

    loguru.logger.info("Failed to locate the News link or headline")
    return ""

def load_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {}
    except json.JSONDecodeError:
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

    if today_date in current_data:
        current_data[today_date].append(data_point)
    else:
        current_data[today_date] = [data_point]

    save_data(data_file_path, current_data)
    loguru.logger.info(f"Scraped and saved: {data_point}")

if __name__ == "__main__":
    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    main()

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")

