from dateutil import parser
from src.web_scraper.base_news_scraper import BaseNewsScraper


class AnthropicNewsScraper(BaseNewsScraper):
    def __init__(self):
        super().__init__(
            base_url='https://www.anthropic.com/news/',
            source='ANTHROPIC'
        )

    def _extract_main_content(self):
        page = self.fetcher.fetch(self.base_url)
        main_content = page.css_first('div.PostList_b-postList___Ngqa')
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
        article_title = article.css_first('h3.PostCard_post-heading__Ob1pu')
        return article_title.text.strip() if article_title else "No Title"

    def _extract_url(self, article):
        url = article.attrib.get('href', '').strip() if article else "No URL"
        return self._normalize_url(url)

    @staticmethod
    def _normalize_url(url):
        if url and not url.startswith("http"):
            url = f"https://www.anthropic.com{url}"
        return url

    def _extract_publish_date(self, article):
        article_date = article.css_first('div.PostList_post-date__djrOA')
        if article_date:
            raw_date = article_date.text.strip()
            try:
                return parser.parse(raw_date, dayfirst=True).isoformat() + 'Z'
            except Exception as e:
                print(f"Error parsing date: {e}")
                return None
        return None

    def _extract_article_content(self, article_url):
        try:
            page = self.fetcher.fetch(article_url)
            if page.status != 200:
                print(f"Error: Page {article_url} could not be loaded (Status Code: {page.status})")
                return None

            article_html = page.css_first('article')
            if not article_html:
                print(f"Error: Content div not found: {article_url}")
                return None

            content_paragraphs = article_html.css('p.ReadingDetail_reading-column__h6GuA')
            content_list_items = article_html.css('ul.ReadingDetail_reading-column__h6GuA li')

            paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
            list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

            return "".join(paragraphs + list_items)
        except Exception as e:
            print(f"Error: {e}")
            return None


if __name__ == '__main__':
    scraper = AnthropicNewsScraper()
    scraper.scrape()
