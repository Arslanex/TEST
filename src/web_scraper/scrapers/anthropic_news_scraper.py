from dateutil import parser
from scrapling import StealthyFetcher


class AnthropicNewsScaper():
    def __init__(self):
        self.fetcher = StealthyFetcher(auto_match=False)
        self.base_url = 'https://www.anthropic.com/news/'

        self.article_data = []

    def _extract_page(self):
        page = self.fetcher.fetch(self.base_url)
        print("Status Code:", page.status)
        return page

    def _extract_main_content(self):
        main_content = self._extract_page().css_first('div.PostList_b-postList___Ngqa')
        if not main_content:
            print(f'Main content not found in {self.base_url}')
            return -1

        return main_content

    def _extract_articles(self):
        main_content = self._extract_main_content()
        if main_content == -1:
            return -1

        return main_content.css('a')

    def _extract_article_elements(self):
        articles = self._extract_articles()
        if articles == -1:
            return -1

        for article in articles:
            article_title = self._extract_title(article)
            article_url = self._extract_url(article)
            article_publish_date = self._extract_publish_date(article)
            article_content = self._extract_article_content(article_url)

            article_data = {
                'article_name': article_title,
                'article_link': article_url,
                'publish_date': article_publish_date,
                'content': article_content
            }

            self._print_article_detail(article_data)
            self.article_data.append(article_data)

    def _extract_title(self, article):
        article_title = article.css_first('h3.PostCard_post-heading__Ob1pu')
        title = article_title.text.strip() if article_title else "No Title"
        return title

    def _extract_url(self, article):
        url = article.attrib.get('href', '').strip() if article else "No URL"
        return self._normalize_url(url)

    def _normalize_url(self, url):
        if url and not url.startswith("http"):
            url = f"https://www.anthropic.com{url}"
        return url

    def _extract_publish_date(self, article):
        article_date = article.css_first('div.PostList_post-date__djrOA')
        publish_date = None

        if article_date:
            raw_date = article_date.text.strip()  # Tarih metnini al
            try:
                # Tarihi Türkçe ay isimleriyle işlemek için locale ayarını dikkate al
                publish_date = parser.parse(raw_date, dayfirst=True).isoformat() + 'Z'
            except Exception as e:
                print(f"Error parsing date: {e}")
                publish_date = None

        return publish_date

    def _extract_article_content(self, article_url):
        try:
            page = self.fetcher.fetch(article_url)
            if page.status != 200:
                print(f"  Hata: Sayfa {article_url} başarıyla yüklenemedi (Status Code: {page.status})")
                return None

            article_html = page.css_first('article')
            if not article_html:
                print(f"  Hata: İçerik div bulunamadı: {article_url}")
                return None

            content_paragraphs = article_html.css('p.ReadingDetail_reading-column__h6GuA')
            content_list_items = article_html.css('ul.ReadingDetail_reading-column__h6GuA li')

            paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
            list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

            content = "".join(paragraphs + list_items)

            return content
        except Exception as e:
            print(f"  Hata: {e}")
            return None

    def _print_article_detail(self, article):
        print("\n" +"=" * 50)
        print(f"Title: {article['article_name']}")
        print(f"URL: {article['article_link']}")
        print(f"Publish Date (ISO): {article['publish_date']}")
        print(f"Content: {article['content']}")
        print("=" * 50)

    def scrape(self):
        self._extract_article_elements()
        return self.article_data


if __name__ == '__main__':
    scraper = AnthropicNewsScaper()
    scraper.scrape()