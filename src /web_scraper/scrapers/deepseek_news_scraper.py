import time
from dateutil import parser
from scrapling import StealthyFetcher

fetcher = StealthyFetcher(auto_match=False)
page = fetcher.fetch('https://www.deepseekv3.com/en/blog')
print("Status Code:", page.status)

main_content = page.css_first('div.min-h-screen')

if not main_content:
    print(main_content.text)
    exit()

# Makaleleri tutmak için liste
articles = []

# 'grid gap-8' içindeki tüm <article> öğelerini seç
article_elements = page.css('div.grid.gap-8 article')

for article in article_elements:
    # Başlığı ve URL'yi al
    title_element = article.css_first('a h2')
    title = title_element.text.strip() if title_element else "No Title"

    url_element = article.css_first('a')
    url = url_element.attrib.get('href', '').strip() if url_element else "No URL"
    if url and not url.startswith("http"):  # Göreceli URL'leri tam URL'ye çevir
        url = f"https://www.deepseekv3.com/{url}"

    # Tarihi al ve ISO formatına dönüştür
    publish_date = "No Date"
    date_element = article.css_first('div.text-gray-600')
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

etailed_articles = []
seen = set()

for idx, article in enumerate(articles, start=1):
    url = article['article_link']
    print(f"({idx}/{len(articles)}) Makale çekiliyor: {url}")

    try:
        page = fetcher.fetch(url)
        if page.status != 200:
            print(f"  Hata: Sayfa {url} başarıyla yüklenemedi (Status Code: {page.status})")

        # İçerik div'ini bul
        article_html = page.css_first('article.prose')
        if not article_html:
            print(f"  Hata: İçerik div bulunamadı: {url}")

        # Paragrafları seç
        content_paragraphs = article_html.css('p')
        paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]

        # Liste öğelerini seç (eğer varsa)
        content_list_items = article_html.css('li')
        list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

        # Başlık, paragraflar ve liste öğe lerini birleştir
        content = "".join(paragraphs + list_items)

        print("\n" + "-" * 50)
        print(f"  İçerik Uzunluğu: {len(content)} karakter")
        print(f"  İçerik:\n{content}")

        # Gecikme (isteğe bağlı)
        time.sleep(1)


    except AttributeError as e:
        print(f"  Hata: HTML element beklenenden farklı: {e}")
    except Exception as e:
        print(f"  Hata: {e}")

