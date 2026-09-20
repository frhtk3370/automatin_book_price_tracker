"""
Book Price Tracker
-------------------
Scrapes book data (title, price, availability, rating) from books.toscrape.com,
saves it as a dated CSV snapshot, and compares it against the previous snapshot
to report any price changes.

Usage:
    python book_price_tracker.py

This script is a learning/portfolio project: books.toscrape.com is a public
sandbox site built specifically for scraping practice, so there are no
restrictions here. Before scraping a real website, always check its
robots.txt and Terms of Service first.
"""

import os
import time
from datetime import date

import requests
import pandas as pd
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 50
HISTORY_FOLDER = "price_history"
REQUEST_DELAY_SECONDS = 1


def scrape_page(url):
    """Scrapes a single page and returns its book data as a list of dicts."""
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")
    page_data = []

    for book in books:
        title = book.h3.a["title"]
        product_url = book.h3.a["href"]
        price = book.find("p", class_="price_color").text.replace("£", "")
        availability = book.find("p", class_="instock availability").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]

        page_data.append({
            "title": title,
            "product_url": product_url,
            "price": float(price),
            "availability": availability,
            "rating": rating,
        })

    return page_data


def scrape_all_pages(base_url, total_pages):
    """Loops through every page and combines the results into one list."""
    all_data = []

    for page_num in range(1, total_pages + 1):
        url = base_url.format(page_num)
        try:
            page_data = scrape_page(url)
            all_data.extend(page_data)
            print(f"Page {page_num} done — {len(page_data)} books")
        except Exception as e:
            print(f"Page {page_num} failed: {e}")

        time.sleep(REQUEST_DELAY_SECONDS)

    return all_data


def save_snapshot(df, folder=HISTORY_FOLDER):
    """Saves a CSV file tagged with today's date and returns its path."""
    os.makedirs(folder, exist_ok=True)
    today = date.today().isoformat()
    filepath = f"{folder}/books_{today}.csv"
    df.to_csv(filepath, index=False)
    print(f"Saved: {filepath}")
    return filepath


def compare_prices(old_path, new_df):
    """Compares a previous snapshot against new data and returns changed prices.

    Matching is done on 'product_url' rather than 'title', because the site
    can contain multiple books with the same title — matching on title alone
    would produce incorrect (cartesian) matches.
    """
    old_df = pd.read_csv(old_path)

    merged = old_df.merge(new_df, on="product_url", suffixes=("_old", "_new"))
    merged["price_change"] = merged["price_new"] - merged["price_old"]
    changed = merged[merged["price_change"] != 0]

    return changed[["title_new", "price_old", "price_new", "price_change"]]


def find_latest_snapshot(folder=HISTORY_FOLDER, exclude=None):
    """Finds the most recent snapshot file in the folder (excluding one path)."""
    if not os.path.isdir(folder):
        return None

    files = sorted(f for f in os.listdir(folder) if f.endswith(".csv"))
    files = [f for f in files if f"{folder}/{f}" != exclude]

    if not files:
        return None

    return f"{folder}/{files[-1]}"


def main():
    print("Starting scrape...\n")
    all_data = scrape_all_pages(BASE_URL, TOTAL_PAGES)
    df = pd.DataFrame(all_data)
    print(f"\nScraped {len(df)} books in total.")

    today_path = save_snapshot(df)

    previous_path = find_latest_snapshot(exclude=today_path)
    if previous_path is None:
        print("\nNo previous snapshot found to compare against. "
              "Price changes will be reported the next time this script runs.")
        return

    print(f"\nComparing against previous snapshot: {previous_path}")
    changes = compare_prices(previous_path, df)

    if changes.empty:
        print("No price changes detected.")
    else:
        print(f"\n{len(changes)} book(s) had a price change:\n")
        print(changes.to_string(index=False))


if __name__ == "__main__":
    main()
