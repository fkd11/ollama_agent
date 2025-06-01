 # Weaviateのコレクションを作成し、データを追加するスクリプト 
import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization

# クライアント接続
client = weaviate.connect_to_local()

try:
    # 既存のコレクション一覧を確認（修正版）
    collections = client.collections.list_all()
    print("既存のコレクション:", collections)
    
    # Questionコレクションが存在する場合は削除
    if "Question" in collections:
        client.collections.delete("Question")
        print("Questionコレクションを削除しました")
    
    # 新しいコレクションを作成
    questions = client.collections.create(
        name="Question",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(     # Configure the Ollama embedding integration
        api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
        model="bge-m3:latest",                               # The model to use
        ),
        generative_config=Configure.Generative.ollama(              # Configure the Ollama generative integration
            api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
            model="qwen3:0.6b",                                       # The model to use
        ),
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                vectorize_property_name=True,  # Use "title" as part of the value to vectorize
                tokenization=Tokenization.LOWERCASE  # Use "lowecase" tokenization
            ),
            Property(
                name="body",
                data_type=DataType.TEXT,
                skip_vectorization=True,  # Don't vectorize this property
                tokenization=Tokenization.WHITESPACE  # Use "whitespace" tokenization
            ),
        ]
        
    )
    print("Questionコレクションを作成しました")
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    
finally:
    # 必ず接続を閉じる
    client.close()


# add data
import weaviate
import requests, json
import MeCab

client = weaviate.connect_to_local()

resp = requests.get(
    "https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json"
)
data = json.loads(resp.text)

questions = client.collections.get("Question")

with questions.batch.fixed_size(batch_size=200) as batch:
    for d in data:
        

        # ストップワード例（日本語）
        stopwords = {"は", "が", "を", "に", "と", "の", "です", "ます", "で", "する"}

        tagger = MeCab.Tagger("-Owakati")
        text = "私はAIが大好きです"
        tokens = tagger.parse(text).strip().split()

        filtered = [tok for tok in tokens if tok not in stopwords]
        final_text = " ".join(filtered)

        batch.add_object(
            {
                "answer": d["Answer"],
                "question": d["Question"],
                "category": d["Category"],
            }
        )
        if batch.number_errors > 10:
            print("Batch import stopped due to excessive errors.")
            break

failed_objects = questions.batch.failed_objects
if failed_objects:
    print(f"Number of failed imports: {len(failed_objects)}")
    print(f"First failed object: {failed_objects[0]}")

client.close()  # Free up resources








# # query data
# import weaviate
# import json

# client = weaviate.connect_to_local()

# questions = client.collections.get("Question")

# response = questions.query.near_text(
#     query="language",
#     limit=2
# )

# for obj in response.objects:
#     print(json.dumps(obj.properties, indent=2))

# client.close()  # Free up resources


# generate data
# import weaviate

# client = weaviate.connect_to_local()

# questions = client.collections.get("Question")

# response = questions.generate.near_text(
#     query="biology",
#     limit=2,
#     grouped_task="Write a tweet with emojis about these facts."
# )

# print(response.generated)  # Inspect the generated text

# client.close()  # Free up resources


# near text query with metadata
import weaviate
from weaviate.classes.query import MetadataQuery

client = weaviate.connect_to_local()

questions = client.collections.get("Question")
response = questions.query.bm25(
    query="Science", 
    limit=10,
    return_metadata=MetadataQuery(score=True),
)

for o in response.objects:
    print(o.properties)  # View the returned properties
    print(o.metadata.score)

client.close()  # Free up resources