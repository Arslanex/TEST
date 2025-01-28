import time
from dateutil import parser
from scrapling import StealthyFetcher


fetcher = StealthyFetcher(auto_match=False)
page = fetcher.fetch('https://www.anthropic.com/news')
print("Status Code:", page.status)

# İlgili Bölüm
main_content = page.css_first('section.Section_section-wrapper__7hN5D')
main_content = page.css_first('div.PostList_b-postList___Ngqa')

if not main_content:
    print(main_content.text)
    exit()

links_in_results = main_content.css('a')

articles = []
seen = set()

for link in links_in_results:
    heading = link.css_first('h3.PostCard_post-heading__Ob1pu')
    article_name = heading.text.strip() if heading else "No Title"

    article_href = link.attrib.get('href', '').strip()

    date_div = link.css_first('div.PostList_post-date__djrOA')  # Tarihi içeren div
    publish_date_iso = None

    if date_div:
        raw_date = date_div.text.strip()  # Tarih metnini al
        try:
            # Tarihi Türkçe ay isimleriyle işlemek için locale ayarını dikkate al
            publish_date_iso = parser.parse(raw_date, dayfirst=True).isoformat() + 'Z'
        except Exception as e:
            print(f"Error parsing date: {e}")
            publish_date_iso = "Unknown Date"

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
    url = f"https://www.anthropic.com{article['article_link']}"
    print(f"({idx}/{len(articles)}) Makale çekiliyor: {url}")

    try:
        page = fetcher.fetch(url)
        if page.status != 200:
            print(f"  Hata: Sayfa {url} başarıyla yüklenemedi (Status Code: {page.status})")
            continue

        article_html = page.css_first('article')

        content_paragraphs = article_html.css('p.ReadingDetail_reading-column__h6GuA')  # Paragraf etiketleri
        content_list_items = article_html.css('ul.ReadingDetail_reading-column__h6GuA li')  # Liste öğeleri

        paragraphs = [p.text.strip() for p in content_paragraphs if p.text.strip()]
        list_items = [li.text.strip() for li in content_list_items if li.text.strip()]

        content = "".join(paragraphs + list_items)  # Her öğe arasında iki satır boşluk

        print('/n' + "-" * 50)
        print(f"  İçerik Uzunluğu: {len(content)} karakter")
        print(f"  İçerik: {content} ")

        time.sleep(1)

    except Exception as e:
        print(f"  Hata: {e}")
        continue