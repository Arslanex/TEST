from dateutil import parser
from src.web_scraper.base_news_scraper import BaseNewsScraper


class GroqNewsScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__(
            base_url='https://groq.com/category/blog/',
            source='GROQ'
        )

    def _extract_main_content(self):
        main_content = self._extract_page().css_first('div.elementor.elementor-3577.elementor-location-archive')
        if not main_content:
            print(f'Main content not found in {self.base_url}')
            return -1

        return main_content

    def _extract_articles(self):
        main_content = self._extract_main_content()
        if main_content == -1:
            return -1

        return main_content.css('div.elementor.elementor-3783')

    def _extract_title(self, article):
        article_title = article.css_first('h2.elementor-heading-title a')
        title = article_title.text.strip() if article_title else "No Title"
        return title

    def _extract_url(self, article):
        article_url = article.css_first('div.elementor-widget-container h2.elementor-heading-title a')
        url = article_url.attrib.get('href', '').strip() if article_url else "No URL"
        return self._normalize_url(url)

    @staticmethod
    def _normalize_url(url):
        if url and not url.startswith("http"):
            url = f"https://groq.com{url}"
        return url

    def _extract_publish_date(self, article):
        article_date = article.css_first('div.elementor-widget-post-info time')
        publish_date = None
        if article_date:
            raw_date = article_date.text.strip()
            try:
                publish_date = parser.parse(raw_date).isoformat() + 'Z'
            except Exception as e:
                publish_date = None
        return publish_date

    def _extract_article_content(self, article_url):
        try:
            page = self.fetcher.fetch(article_url)
            if page.status != 200:
                print(f"  Hata: Sayfa {article_url} başarıyla yüklenemedi (Status Code: {page.status})")
                return None

            article_html = page.css_first('div.elementor-widget-theme-post-content')
            if not article_html:
                print(f"  Hata: İçerik div bulunamadı: {article_url}")
                return None

            content_paragraphs = article_html.css('div.elementor-widget-container p')
            content_list_items = article_html.css('div.elementor-widget-container li')

            paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
            list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

            content = "".join(paragraphs + list_items)

            return content
        except Exception as e:
            print(f"  Hata: {e}")
            return None


if __name__ == '__main__':
    scraper = GroqNewsScraper()
    scraper.scrape()
