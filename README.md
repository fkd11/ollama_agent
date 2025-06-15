unset ROS_DISTRO
unset PYTHONPATH
python -c "import sys; sys.path = [p for p in sys.path if 'ros' not in p.lower()]"





# ollama_agent

## Ollama settings
ollama need to open localport
add OLLAMA_HOST=0.0.0.0:11434 

## weaviate query
- near_text
 :  find objects with the nearest vector to an input text.
- near_object : find similar objects to that object

### vecrot search options

- target_vector
   : restrict the query property
```python
response = reviews.query.near_text(
    query="a sweet German white wine",
    limit=2,
    target_vector="title_country",  # Specify the target vector for named vector collections
    return_metadata=MetadataQuery(distance=True)
)
```

- distance
    : set a similarity threshold between the search and target vectors
```python
response = jeopardy.query.near_text(
    query="animals in movies",
    distance=0.25, # max accepted distance
    return_metadata=MetadataQuery(distance=True)
)
```
- filters
    :narrow your search, for more specific results

### keyword search options
- query_properties
    : can be directed to only search a subset of object properties.

```python
response = jeopardy.query.bm25(
    query="safety",
    query_properties=["question"],
    return_metadata=MetadataQuery(score=True),
    limit=3
)
```

### overrap
over lap needs 10%

### data schema
| Category           | Field                      | Type      | Description                        |
| ------------------ | -------------------------- | --------- | ---------------------------------- |
| 📑 論文／ソースレベル情報     | `paper_id`                 | text      | 社内管理用の一意ID（例：`PAPER-2025-0001`）    |
| 📑 論文／ソースレベル情報     | `title`                    | text      | 論文タイトル                             |
| 📑 論文／ソースレベル情報     | `authors`                  | text\[]   | 著者名リスト                             |
| 📑 論文／ソースレベル情報     | `journal`／`conference`     | text      | 発表先（ジャーナル名または学会名）                  |
| 📑 論文／ソースレベル情報     | `year`                     | int       | 発表年                                |
| 📑 論文／ソースレベル情報     | `doi`／`arXiv_id`           | text      | DOIやarXiv識別子                       |
| 📑 論文／ソースレベル情報     | `url`                      | text      | フルテキストへのリンク                        |
| 📑 論文／ソースレベル情報     | `abstract`                 | text      | 論文の要約部分（全文検索・フィルタ用）                |
| 📑 論文／ソースレベル情報     | `keywords`                 | text\[]   | 著者指定／自動抽出キーワード（ドキュメント全体）           |
| 📌 チャンク固有情報        | `chunk_id`                 | text      | チャンクごとの一意ID                        |
| 📌 チャンク固有情報        | `section`                  | text      | セクション名（例：`Introduction`, `Method`） |
| 📌 チャンク固有情報        | `subsection`               | text      | サブセクション名                           |
| 📌 チャンク固有情報        | `page_number`              | int       | 元PDFのページ番号                         |
| 📌 チャンク固有情報        | `paragraph_number`         | int       | ページ内段落番号                           |
| 📌 チャンク固有情報        | `offset`／`length`          | int       | ドキュメント先頭からの文字オフセットと長さ              |
| 📌 チャンク固有情報        | `token_count`              | int       | トークン数                              |
| 📌 チャンク固有情報        | `chunk_order`              | int       | ドキュメント内での並び順                       |
| 📌 チャンク固有情報        | `language`                 | text      | 言語（例：`ja`／`en`）                    |
| 📌 チャンク固有情報        | `contains_figure_or_table` | bool      | 図表参照があるか                           |
| 📌 チャンク固有情報        | `citations_in_chunk`       | text\[]   | チャンク中に引用されている文献リスト                 |
| 🔍 検索・RAG向け補助情報    | `embedding_model`          | text      | 埋め込み生成に使ったモデル名／バージョン               |
| 🔍 検索・RAG向け補助情報    | `ingestion_date`           | datetime  | チャンクをDBに取り込んだ日時                    |
| 🔍 検索・RAG向け補助情報    | `source_hash`              | text      | 元チャンクのハッシュ値（重複検出用）                 |
| 🔍 検索・RAG向け補助情報    | `tfidf_keywords`           | text\[]   | チャンク単位で抽出したTF-IDF上位キーワード           |
| 🔍 検索・RAG向け補助情報    | `named_entities`           | text\[]   | NERで抽出した固有表現（人物・組織・場所など）           |
| 🔍 検索・RAG向け補助情報    | `topic_label`              | text      | トピックモデル（LDAなど）によるラベル               |
| 🔍 検索・RAG向け補助情報    | `sentiment_score`          | float     | 感情分析スコア（必要に応じて）                    |
| 🔗 リレーション／管理用フィールド | `parent_paper_ref`         | Reference | `Paper`クラスなどへの参照                   |
| 🔗 リレーション／管理用フィールド | `related_chunk_ids`        | text\[]   | 議論の前後関係を示すチャンクIDリスト                |
| 🔗 リレーション／管理用フィールド | `version`                  | int       | ドキュメント更新／再処理用のバージョン番号              |
| 🔗 リレーション／管理用フィールド | `ingested_by`              | text      | 処理を実行したスクリプト or 人                  |
| 🛠️ 拡張・運用上のメタデータ   | `quality_score`            | float     | OCR精度やテキスト抽出の品質推定値                 |
| 🛠️ 拡張・運用上のメタデータ   | `processing_notes`         | text      | 手動補正や例外処理のコメント                     |
| 🛠️ 拡張・運用上のメタデータ   | `access_control`           | text      | 閲覧制限レベル（社内限定／公開可など）                |
| 🛠️ 拡張・運用上のメタデータ   | `usage_count`              | int       | 検索でヒットした回数など統計情報                   |

