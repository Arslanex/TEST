import time
from dateutil import parser
from scrapling import StealthyFetcher

fetcher = StealthyFetcher(auto_match=False)
page = fetcher.fetch('https://x.ai/blog')
print("Status Code:", page.status)

main_content = page.css_first('div.border-top')

if not main_content:
    print(main_content.text)
    exit()

links_in_results = main_content.css('div.col')

articles = []
seen = set()

for post_div in links_in_results:
    # Başlık ve URL'yi al
    title_element = post_div.css_first('a.blog-teaser_heading__KWHU_ h4')
    title = title_element.text.strip() if title_element else "No Title"

    url_element = post_div.css_first('a.blog-teaser_heading__KWHU_')
    url = url_element.attrib.get('href', '').strip() if url_element else "No URL"
    if url and not url.startswith("http"):  # Göreceli URL'leri tam URL'ye çevirin
        url = f"https://x.ai/{url}"

    # Tarihi al ve ISO formatına dönüştür
    publish_date = "No Date"
    date_element = post_div.css_first('div.blog-teaser_timestamp__hb6gF p')
    if date_element:
        raw_date = date_element.text.strip()
        try:
            # Tarihi ISO formatına çevir
            publish_date = parser.parse(raw_date).isoformat() + 'Z'
        except Exception as e:
            publish_date = "Invalid Date"


    # Sonuçları yazdır
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"Publish Date (ISO): {publish_date}")
    print("-" * 50)

    # Makale bilgilerini listeye ekle
    articles.append({
        'article_name': title,
        'article_link': url,
        'publish_date': publish_date,
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

        # İçerik div'ini bul
        article_html = page.css_first('div.col-xxl-6')

        if not article_html:
            print(f"  Hata: İçerik div bulunamadı: {url}")
            continue
        # Paragrafları seç
        content_paragraphs = article_html.css('p')
        paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]

        # Liste öğelerini seç (eğer varsa)
        content_list_items = article_html.css('li')
        list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

        # Başlık, paragraflar ve liste öğelerini birleştir
        content = f"".join(paragraphs + list_items)

        # Sonuçları yazdır
        print("\n" + "-" * 50)
        print(f"  İçerik Uzunluğu: {len(content)} karakter")
        print(f"  İçerik:\n{content}")

        time.sleep(1)


    except Exception as e:
        print(f"  Hata: {e}")
