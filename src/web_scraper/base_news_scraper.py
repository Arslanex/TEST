from abc import ABC, abstractmethod
from dateutil import parser
from scrapling import StealthyFetcher


class BaseNewsScraper(ABC):
    def __init__(self, base_url, source):
        self.fetcher = StealthyFetcher(auto_match=False)
        self.base_url = base_url
        self.source = source
        self.article_data = []

    def _extract_page(self):
        page = self.fetcher.fetch(self.base_url)
        print(f"Status Code for {self.source}: {page.status}")
        return page

    @abstractmethod
    def _extract_main_content(self):
        pass

    @abstractmethod
    def _extract_articles(self):
        pass

    def _extract_article_elements(self):
        articles = self._extract_articles()
        if articles == -1:
            return -1

        for article in articles:
            try:
                article_title = self._extract_title(article)
                article_url = self._extract_url(article)
                article_publish_date = self._extract_publish_date(article)
                article_content = self._extract_article_content(article_url)

                article_data = {
                    'article_source': self.source,
                    'article_name': article_title,
                    'article_link': article_url,
                    'publish_date': article_publish_date,
                    'article_content': article_content
                }

                self._print_article_detail(article_data)
                self.article_data.append(article_data)
            except Exception as e:
                print(f"Error extracting article details: {e}")
                continue

        return self.article_data

    @abstractmethod
    def _extract_title(self, article):
        pass

    @abstractmethod
    def _extract_url(self, article):
        pass

    @abstractmethod
    def _extract_publish_date(self, article):
        pass

    @abstractmethod
    def _extract_article_content(self, article_url):
        pass

    def _print_article_detail(self, article_data):
        print(f"Source: {article_data['article_source']}")
        print(f"Title: {article_data['article_name']}")
        print(f"URL: {article_data['article_link']}")
        print(f"Publish Date: {article_data['publish_date']}")
        print(f"Content Length: {len(article_data['article_content'])}")
        print(f"Content: {article_data['article_content']}")
        print("---")

    def scrape(self):
        return self._extract_article_elements()
