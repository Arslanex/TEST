import time
from dateutil import parser
from scrapling import StealthyFetcher

fetcher = StealthyFetcher(auto_match=False)
page = fetcher.fetch('https://ai.meta.com/blog/')
print("Status Code:", page.status)

main_content = page.css_first('div._7h8s')

if not main_content:
    print(main_content.text)
    exit()

links_in_results = main_content.css('div._amda')

articles = []
seen = set()

for post_div in links_in_results:
    # Başlık ve URL'yi al
    title_link = post_div.css_first('a._amcw._amdf')
    title = title_link.text.strip() if title_link else "No Title"
    url = title_link.attrib.get('href', '').strip() if title_link else "No URL"

    # Tarihi al ve ISO formatına dönüştür
    publish_date = "No Date"
    parent_div = post_div.css_first('div._amdc')  # Ebeveyn div'i seç
    if parent_div:
        date_divs = parent_div.css('div._amdj')  # Bu ebeveyn altındaki tarih div'lerini seç
        for div in date_divs:
            if div.text.strip():
                raw_date = div.text.strip()
                try:
                    # Tarihi ISO formatına çevir
                    publish_date = parser.parse(raw_date).isoformat() + 'Z'
                except Exception as e:
                    publish_date = "Invalid Date"
                break  # İlk bulunan tarihi al ve döngüyü sonlandır

    # Sonuçları yazdır
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"Publish Date (ISO): {publish_date}")
    print("-" * 50)

    articles.append({
        'article_name': title,
        'article_link': url,
        'publish_date': publish_date  # None ise JSON'da null görünecek
    })

detailed_articles = []
seen = set()

for idx, article in enumerate(articles, start=1):
    url = article['article_link']
    print(f"({idx}/{len(articles)}) Makale çekiliyor: {url}")

    try:
        page = fetcher.fetch(url)
        if page.status != 200:
            print(f"  Hata: Sayfa {url} başarıyla yüklenemedi (Status Code: {page.status})")
            continue

        # Ana makale div'ini seç
        article_html = page.css_first('div._a5ci')
        if not article_html:
            print(f"  Hata: İçerik div bulunamadı: {url}")
            continue

        # Paragrafları ve liste öğelerini seç
        content_paragraphs = article_html.css('p')
        content_list_items = article_html.css('li')

        # Paragrafları ve liste öğelerini temizle
        paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
        list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

        # İçeriği birleştir
        content = "".join(paragraphs + list_items)

        print("" + "-" * 50)
        print(f"  İçerik Uzunluğu: {len(content)} karakter")
        print(f"  İçerik:\n{content}")

        time.sleep(1)

    except Exception as e:
        print(f"  Hata: {e}")
        continue
