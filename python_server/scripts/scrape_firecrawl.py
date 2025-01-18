import firecrawl
from config import FIRECRAWL_API_KEY
from scripts.urls import urls


def scrape_firecrawl(url: str) -> str:
    app = firecrawl.FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    try:
        scraped_data = app.scrape_url(url=url, params={"pageOptions": {"onlyMainContent": True}})["markdown"]
    except Exception as e:
        # Check if the error is specifically a 429 status code
        if "429" in str(e):
            raise  # Re-raise the exception if it is 429 to trigger retry
        else:
            raise Exception(f"An unexpected error occurred: {str(e)}")
    return scraped_data

# poetry run python pinecone_ingestion.py
if __name__ == "__main__":
    

