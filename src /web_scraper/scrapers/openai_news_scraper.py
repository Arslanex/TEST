import re
import time
from dateutil import parser
from scrapling import StealthyFetcher



fetcher = StealthyFetcher( auto_match=False)
page = fetcher.fetch('https://openai.com/news/')
print("Status Code:", page.status)

# İlgili Bölüm
results_div = page.css_first('#results')
if not results_div:
    print("id='results' olan <div> bulunamadı!")
    exit()

# Kartlar
links_in_results = results_div.css('a')

articles = []
seen = set()

for link in links_in_results:
    article_name = link.attrib.get('aria-label', '').strip()
    article_href = link.attrib.get('href', '').strip()

    # Aynı (başlık, link) verisini tekrar eklemeyelim
    if article_name and article_href and (article_name, article_href) not in seen:
        seen.add((article_name, article_href))

    date_span = link.find('span', lambda el: re.search(r'\b\d{4}\b', el.text))
    publish_date_iso = None

    if date_span:
        raw_date = date_span.text.strip()  # "Dec 27, 2024" gibi
        try:
            dt = parser.parse(raw_date)  # datetime objesine çevir
            publish_date_iso = dt.isoformat()  # "2024-12-27T00:00:00"
        except Exception:
            # Pars edilemezse None olarak bırakalım
            pass

    # Sonuçları yazdır
    print(f"\nArticle Name: {article_name}")
    print(f"Article Link: {article_href}")
    print(f"Publish Date: {publish_date_iso}")

    articles.append({
        'article_name': article_name,
        'article_link': article_href,
        'publish_date': publish_date_iso  # None ise JSON'da null görünecek
    })


detailed_articles = []
seen = set()

for idx, article in enumerate(articles, start=1):
    url = f"https://openai.com{article['article_link']}"
    print(f"({idx}/{len(articles)}) Makale çekiliyor: {url}")

    try:
        page = fetcher.fetch(url)
        if page.status != 200:
            print(f"  Hata: Sayfa {url} başarıyla yüklenemedi (Status Code: {page.status})")
            continue

        article_html = page.css_first('article.mt-2xl')
        if not article_html:
            print(f"  Hata: <article> etiketi bulunamadı: {url}")
            continue

        content_spans = article_html.css('div.prose p span')
        content_list_items = article_html.css('div.prose li')

        paragraphs = [span.text.strip() for span in content_spans if span.text.strip()]
        list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

        content = "".join(paragraphs + list_items)

        print('/n'+"-"*50)
        print(f"  İçerik Uzunluğu: {len(content)} karakter")
        print(f"  İçerik: {content} ")

        time.sleep(1)

    except Exception as e:
        print(f"  Hata: {e}")
        continue