import weaviate
import requests
from typing import Any, List
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Document

# --- Step 1: Ollama Embedding 定義 ---
# Ollama埋め込みモデルの設定
embed_model = OllamaEmbedding(model_name="dengcao/Qwen3-Embedding-0.6B:F16", base_url="http://localhost:11434")

# --- Step 2: Weaviate クライアントと埋め込み設定 ---
client = weaviate.connect_to_local()

embedding = OllamaEmbedding(api_url="http://localhost:11434", model_name="dengcao/Qwen3-Embedding-0.6B:F16")
vector_store = WeaviateVectorStore(
    weaviate_client=client,
    embedding=embedding,
    index_name="OllamaPDFIndex",
    text_key="content"
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# --- Step 3: PDF 読み込みとチャンク分割 ---
reader = PyMuPDFReader()
documents: List[Document] = reader.load(file_path="./pdf/sample.pdf")

# Sentenceベースのチャンク（長さと重複は調整可能）
parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)

# --- Step 4: チャンクを Weaviate に格納 ---
index = VectorStoreIndex(nodes, storage_context=storage_context,embed_model=embedding)
