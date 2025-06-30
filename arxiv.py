import feedparser
import requests
import time
import random
import os
from datetime import datetime

query = "magnetocaloric"
output_dir = "pdf"
os.makedirs(output_dir, exist_ok=True)

BATCH_SIZE = 100
BASE_URL = "http://export.arxiv.org/api/query"

start = 0
total_results = None

while True:
    url = f"{BASE_URL}?search_query=all:{query}&start={start}&max_results={BATCH_SIZE}"
    print(f"\n🔍 Fetching: start={start}")
    feed = feedparser.parse(url)

    # 最初の1回だけトータル件数取得
    if total_results is None:
        total_results = int(feed.feed.opensearch_totalresults)
        print(f"📚 Total results: {total_results}")

    if not feed.entries:
        print("✅ No more entries found. Done.")
        break

    for i, entry in enumerate(feed.entries):
        try:
            title = entry.title.strip()
            authors = [author['name'] for author in entry.authors]
            date = entry.published
            dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            year = dt.year
            link = entry.links[0].href
            pdf_url = entry.links[1].href

            meta_json = {
                "title": title,
                "authors": authors,
                "link": link,
                "update_date": date,
            }
            print(f"📥 Downloading: {meta_json['title']}")

            # ファイル名整形
            file_name = title.replace(" ", "_").replace("\n", "").replace("/", "_")
            file_path = os.path.join(output_dir, f"{file_name}.pdf")

            # スリープを入れてマナーを守る
            time.sleep(random.uniform(1.5, 3.5))

            # PDFをダウンロード
            response = requests.get(pdf_url)
            with open(file_path, "wb") as f:
                f.write(response.content)

        except Exception as e:
            print(f"❌ Error downloading '{entry.title}': {e}")

    start += BATCH_SIZE
    if start >= total_results:
        print("✅ All documents processed.")
        break

    # バッチごとに少し長めにスリープ
    time.sleep(5)



# import time
# import random
# from datetime import datetime
# import requests
# import feedparser

# query = "magnetocaloric+material"
# # url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3"
# url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3"

# feed = feedparser.parse(url)

# for i, entry in enumerate(feed.entries):
#     title = entry.title
#     authors = [author['name'] for author in entry.authors]
#     date = entry.published
#     dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
#     year = dt.year
#     link = entry.links[0].href

#     meta_json = {
#         "title": title,
#         "authors": authors,
#         "link": link,
#         "update_date": date,
#     }
#     print(f"Downloading: {meta_json}")

#     file_name = entry.title.replace(" ", "_").replace("\n", "").replace("/", "_")  # ファイル名用に整形
#     pdf_url = entry.links[1].href
    
#     time.sleep(random.uniform(1.5, 3.5))
#     response = requests.get(pdf_url)
#     with open(f"pdf/{file_name}.pdf", "wb") as f:
#         f.write(response.content)



