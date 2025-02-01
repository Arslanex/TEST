from src.web_scraper.sites.anthropic_news_scraper import AnthropicNewsScraper
from src.web_scraper.sites.deepseek_news_scraper import DeepSeekNewsScraper
from src.web_scraper.sites.groq_news_scraper import GroqNewsScraper
from src.web_scraper.sites.grok_news_scraper import GrokNewsScraper
from src.web_scraper.sites.meta_news_scraper import MetaNewsScraper
from src.web_scraper.sites.openai_news_scraper import OpenAINewsScraper
from models.article import Article
from database.config import DatabaseConfig
from database.crud.article_crud import ArticleCRUD
import asyncio
import time


scrapers = [
    AnthropicNewsScraper,
    DeepSeekNewsScraper,
    GroqNewsScraper,
    GrokNewsScraper,
    MetaNewsScraper,
    OpenAINewsScraper,
]


async def main():
    # Initialize the MongoDB connection
    DatabaseConfig.initialize()

    # Create an instance of your scraper
    for i, scraper in enumerate(scrapers):
        # Add a delay between scraping attempts (skip delay for first scraper)
        if i > 0:
            print(f"\nWaiting 5 seconds before starting next scraper...")
            time.sleep(5)  # 5 second delay between scrapers

        print(f"\nStarting scraper: {scraper.__name__}")
        
        # Run the synchronous scrape() method in a separate thread
        scraped_articles = await asyncio.to_thread(scraper().scrape)

        # Create an instance of your CRUD handler
        article_crud = ArticleCRUD()

        # Loop through the scraped articles
        for article_data in scraped_articles:
            try:
                # Create Article instance with the exact field names from the scraper
                article = Article(**article_data)  # The field names now match exactly

                # Check for duplicate articles by URL
                duplicate = await article_crud.find_duplicates(article)
                if duplicate:
                    print(f"Article already exists: {article.article_link}")
                else:
                    # Insert the article into the database
                    await article_crud.create(article)
                    print(f"Inserted article: {article.article_link}")
            except Exception as e:
                print(f"Error processing article: {e}")

    # Close the MongoDB connection
    DatabaseConfig.close()


if __name__ == '__main__':
    asyncio.run(main())