import json
import sys

import firecrawl
from config import FIRECRAWL_API_KEY
from scripts.urls import urls


def scrape_firecrawl(url: str) -> dict:
    """
    Scrapes a given URL using FirecrawlApp.
    If a 429 error occurs, it's re-raised for potential retries.
    """
    app = firecrawl.FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    try:
        scraped_data = app.scrape_url(
            url=url,
            params={
                "formats": ["markdown"],
                "onlyMainContent": True,
            },
        )
    except Exception as e:
        # Check if the error is specifically a 429 status code
        if "429" in str(e):
            raise  # Re-raise the exception if it is 429 to trigger retry
        else:
            raise Exception(f"An unexpected error occurred: {str(e)}")
    return scraped_data


def save_json(filename: str, data: list):
    """
    Saves the given data (list of dicts) as a JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main(output_filename: str):
    """
    1. Iterates over all URLs in `urls`.
    2. Scrapes each URL using `scrape_firecrawl`.
    3. Collects the results into a list.
    4. Saves the final list to `output_filename` as JSON.
    """
    all_scraped_data = []
    for url in urls:
        print(f"Scraping: {url}")
        try:
            data = scrape_firecrawl(url)
            all_scraped_data.append(data)
        except Exception as err:
            print(f"Failed to scrape {url}: {err}")

    # Save the aggregated data to JSON
    save_json(output_filename, all_scraped_data)
    print(f"Scraped data saved to {output_filename}")

# poetry run python -m scripts.scrape_firecrawl
if __name__ == "__main__":
    # Allow an optional command-line argument for the output filename,
    # or default to "scraped_data.json"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "scraped_data.json"

    main(filename)
