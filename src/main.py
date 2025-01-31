from src.web_scraper.sites.anthropic_news_scraper import AnthropicNewsScraper
from src.web_scraper.sites.deepseek_news_scraper import DeepSeekNewsScraper
from src.web_scraper.sites.groq_news_scraper import GroqNewsScraper
from src.web_scraper.sites.grok_news_scraper import GrokNewsScraper
from src.web_scraper.sites.meta_news_scraper import MetaNewsScraper
from src.web_scraper.sites.openai_news_scraper import OpenAINewsScraper

scrappers = [
    AnthropicNewsScraper,
    DeepSeekNewsScraper,
    GroqNewsScraper,
    GrokNewsScraper,
    MetaNewsScraper,
    OpenAINewsScraper
    ]

def scrape(web_scraper):
    scraper = web_scraper()
    return scraper.scrape()

for i in scrappers:
    scrape(i)