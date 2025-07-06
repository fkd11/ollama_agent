import feedparser
import requests
import time
import random
import os
from datetime import datetime

query = "heat storage material"
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
                "file_name": file_name,
            }
            now = datetime.now()
            print(now)
            print(f"📥 Downloading: {meta_json['title']}")
            

            # ファイル名整形
            file_name = title.replace(" ", "_").replace("\n", "").replace("/", "_")
            file_path = os.path.join(output_dir, f"{file_name}.pdf")

            

            # PDFをダウンロード
            response = requests.get(pdf_url)
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            # スリープを入れる
            time.sleep(random.uniform(1.5, 3.5))

        except Exception as e:
            print(f"❌ Error downloading '{entry.title}': {e}")

    start += BATCH_SIZE
    if start >= total_results:
        print("✅ All documents processed.")
        break

    # バッチごとに少し長めにスリープ
    time.sleep(5)

