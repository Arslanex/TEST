import re
from dateutil import parser
from src.web_scraper.base_news_scraper import BaseNewsScraper


class OpenAINewsScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__(
            base_url='https://openai.com/news/',
            source='OPENAI'
        )

    def _extract_main_content(self):
        main_content = self._extract_page().css_first('#results')
        if not main_content:
            print(f'Main content not found in {self.base_url}')
            return -1

        return main_content

    def _extract_articles(self):
        main_content = self._extract_main_content()
        if main_content == -1:
            return -1

        return main_content.css('a')

    def _extract_title(self, article):
        article_title = article.attrib.get('aria-label', '').strip()
        title = article_title if article_title else "No Title"
        return title

    def _extract_url(self, article):
        url = article.attrib.get('href', '').strip() if article else "No URL"
        return self._normalize_url(url)

    def _normalize_url(self, url):
        if url and not url.startswith("http"):
            url = f"https://openai.com{url}"
        return url

    def _extract_publish_date(self, article):
        article_date = article.find('span', lambda el: re.search(r'\b\d{4}\b', el.text))
        publish_date = None

        if article_date:
            raw_date = article_date.text.strip()
            try:
                dt = parser.parse(raw_date)
                publish_date = dt.isoformat()
            except Exception:
                pass
        return publish_date

    def _extract_article_content(self, article_url):
        try:
            page = self.fetcher.fetch(article_url)
            if page.status != 200:
                print(f"  Hata: Sayfa {article_url} başarıyla yüklenemedi (Status Code: {page.status})")
                return None

            article_html = page.css_first('article.mt-2xl')
            if not article_html:
                print(f"  Hata: İçerik div bulunamadı: {article_url}")
                return None

            content_paragraphs = article_html.css('div.prose p span')
            content_list_items = article_html.css('div.prose li')

            paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
            list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

            content = "".join(paragraphs + list_items)

            return content
        except Exception as e:
            print(f"  Hata: {e}")
            return None


if __name__ == '__main__':
    scraper = OpenAINewsScraper()
    scraper.scrape()
