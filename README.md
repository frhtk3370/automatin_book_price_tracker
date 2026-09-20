# Book Price Tracker

A Python web scraper that collects book data (title, price, availability,
rating) from [books.toscrape.com](https://books.toscrape.com/), saves it as
a dated CSV snapshot, and compares it against the previous snapshot to
detect price changes over time.

## What this project demonstrates

- HTML scraping with `requests` + `BeautifulSoup`
- Handling pagination across a full site catalog (50 pages / ~1000 items)
- Data cleaning with `pandas` (type conversion, encoding fixes)
- A data-quality check before merging two datasets (see the walkthrough
  notebook — matching on `title` alone produced incorrect results due to
  duplicate titles in the catalog; fixed by matching on a unique product URL
  instead)
- Basic error handling and rate-limiting (`try/except`, `time.sleep`)
- Turning exploratory code into a clean, reusable script

## Files

| File | Description |
|---|---|
| `book_price_tracker.py` | Final, production-ready script. Run directly to scrape the catalog, save a snapshot, and report price changes against the previous run. |
| `book_price_tracker_walkthrough.ipynb` | Step-by-step notebook showing how the script was built and the reasoning behind each design decision. |

## Usage

```bash
pip install requests beautifulsoup4 pandas
python book_price_tracker.py
```

The first run saves a snapshot with no comparison (nothing to compare
against yet). Each subsequent run reports any price changes since the last
snapshot.

## Notes

`books.toscrape.com` is a public sandbox site built specifically for
scraping practice — no restrictions apply. Before scraping a real website,
always check its `robots.txt` and Terms of Service.

## Adapting this for a real project

This scraper is built around one site's HTML structure, but the same
pattern — request → parse → extract → paginate → clean → track changes —
applies to most e-commerce price-tracking projects. Get in touch if you'd
like this adapted to a specific website.
