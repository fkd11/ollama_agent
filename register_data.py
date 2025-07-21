# Weaviateのコレクションを作成し、データを追加するスクリプト 
# import weaviate_control
import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization


WEAVIATE_SCHEMA = {
    "classes": [
        {
            "class": "Document",
            "description": "学術文献のメタデータ",
            "vectorizer_config": [
                {
                    "name": "general_vector",
                    "vectorizer": {
                        "text2vec-ollama": {
                            "apiEndpoint": "http://host.docker.internal:11434",
                            "model": "dengcao/Qwen3-Embedding-0.6B:F16"
                        }
                    }
                }
            ],
            "generative_config": {
                "ollama": {
                    "apiEndpoint": "http://host.docker.internal:11434",
                    "model": "qwen3:0.6b"
                }
            },
            "properties": [
                # 基本メタデータ
                {"name": "document_id", "dataType": ["text"], "description": "文書の一意識別子", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "title", "dataType": ["text"], "description": "文献タイトル", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "abstract", "dataType": ["text"], "description": "要約", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "authors", "dataType": ["text[]"], "description": "著者リスト", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "affiliations", "dataType": ["text[]"], "description": "所属機関", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "publication_date", "dataType": ["date"], "description": "発行日", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "journal_name", "dataType": ["text"], "description": "雑誌名", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "volume", "dataType": ["text"], "description": "巻号", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "issue", "dataType": ["text"], "description": "号", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "pages", "dataType": ["text"], "description": "ページ範囲", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "doi", "dataType": ["text"], "description": "DOI", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "arxiv_id", "dataType": ["text"], "description": "arXiv ID", "vectorizePropertyName": False, "skipVectorization": True},
                
                # 全文データ管理
                {"name": "has_full_text", "dataType": ["boolean"], "description": "全文データの有無", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "full_text_storage_type", "dataType": ["text"], "description": "全文保存方式", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "full_text_url", "dataType": ["text"], "description": "全文アクセスURL", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "full_text_hash", "dataType": ["text"], "description": "全文のハッシュ値", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "license_type", "dataType": ["text"], "description": "ライセンス種別", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "access_permission", "dataType": ["text"], "description": "アクセス権限", "vectorizePropertyName": False, "skipVectorization": True},
                
                # 分類情報
                {"name": "keywords", "dataType": ["text[]"], "description": "キーワード", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "research_fields", "dataType": ["text[]"], "description": "研究分野", "vectorizePropertyName": True, "skipVectorization": True},
                
                # システム管理
                {"name": "created_at", "dataType": ["date"], "description": "登録日時", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "updated_at", "dataType": ["date"], "description": "更新日時", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "source_url", "dataType": ["text"], "description": "元データのURL", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "file_path", "dataType": ["text"], "description": "ファイルパス", "vectorizePropertyName": False, "skipVectorization": True},
                
                # 言語・地域情報
                {"name": "language", "dataType": ["text"], "description": "言語", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "country", "dataType": ["text"], "description": "発行国", "vectorizePropertyName": False, "skipVectorization": True},
                
                # 統計情報
                {"name": "word_count", "dataType": ["int"], "description": "単語数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "page_count", "dataType": ["int"], "description": "ページ数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "reference_count", "dataType": ["int"], "description": "参考文献数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "figure_count", "dataType": ["int"], "description": "図表数", "vectorizePropertyName": False, "skipVectorization": True},
            ],
        },
        {
            "class": "Chunk",
            "description": "文献の分割されたテキストチャンク",
            "vectorizer": "text2vec-ollama",  # チャンクのセマンティック検索用
            "properties": [
                # チャンク基本情報
                {"name": "chunk_id", "dataType": ["text"], "description": "チャンクの一意識別子", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "document_id", "dataType": ["text"], "description": "親文書ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "chunk_type", "dataType": ["text"], "description": "チャンク種別", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "content", "dataType": ["text"], "description": "チャンク内容", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "chunk_index", "dataType": ["int"], "description": "文書内での順序", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "section_title", "dataType": ["text"], "description": "セクションタイトル", "vectorizePropertyName": True, "skipVectorization": True},
                
                # 位置情報
                {"name": "start_char", "dataType": ["int"], "description": "開始文字位置", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "end_char", "dataType": ["int"], "description": "終了文字位置", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "page_number", "dataType": ["int"], "description": "ページ番号", "vectorizePropertyName": False, "skipVectorization": True},
                
                # 内容分析
                {"name": "word_count", "dataType": ["int"], "description": "単語数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "sentence_count", "dataType": ["int"], "description": "文数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "entities", "dataType": ["text[]"], "description": "抽出された固有表現", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "key_phrases", "dataType": ["text[]"], "description": "重要フレーズ", "vectorizePropertyName": True, "skipVectorization": True},
                
                # 品質指標
                {"name": "importance_score", "dataType": ["number"], "description": "重要度スコア", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "readability_score", "dataType": ["number"], "description": "可読性スコア", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "semantic_density", "dataType": ["number"], "description": "意味密度", "vectorizePropertyName": False, "skipVectorization": True},
                
                # システム管理
                {"name": "created_at", "dataType": ["date"], "description": "作成日時", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "embedding_model", "dataType": ["text"], "description": "使用した埋め込みモデル", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "processing_version", "dataType": ["text"], "description": "処理バージョン", "vectorizePropertyName": False, "skipVectorization": True},
            ],
            "moduleConfig": {
                # エンベディング設定（Ollama）
                "text2vec-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "dengcao/Qwen3-Embedding-0.6B:F16"
                },
                # ジェネレーティブ設定（Ollama）
                "generative-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "qwen3:0.6b"
                }
            }
        },
        {
            "class": "Author",
            "description": "著者情報",
            "vectorizer": "text2vec-ollama",  # 著者名・研究分野での類似検索
            "properties": [
                {"name": "author_id", "dataType": ["text"], "description": "著者ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "name", "dataType": ["text"], "description": "著者名", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "normalized_name", "dataType": ["text"], "description": "正規化された著者名", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "affiliations", "dataType": ["text[]"], "description": "所属機関履歴", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "orcid", "dataType": ["text"], "description": "ORCID ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "research_interests", "dataType": ["text[]"], "description": "研究興味", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "h_index", "dataType": ["number"], "description": "h-index", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "citation_count", "dataType": ["int"], "description": "総被引用数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "publication_count", "dataType": ["int"], "description": "出版数", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "email", "dataType": ["text"], "description": "メールアドレス", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "homepage", "dataType": ["text"], "description": "ホームページURL", "vectorizePropertyName": False, "skipVectorization": True},
            ],
            "moduleConfig": {
                # エンベディング設定（Ollama）
                "text2vec-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "dengcao/Qwen3-Embedding-0.6B:F16"
                },
                # ジェネレーティブ設定（Ollama）
                "generative-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "qwen3:0.6b"
                }
            }
        },
        {
            "class": "Concept",
            "description": "研究概念・トピック",
            "vectorizer": "text2vec-ollama",  # 概念間の類似性検索
            "properties": [
                {"name": "concept_id", "dataType": ["text"], "description": "概念ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "name", "dataType": ["text"], "description": "概念名", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "description", "dataType": ["text"], "description": "概念の説明", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "synonyms", "dataType": ["text[]"], "description": "同義語", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "category", "dataType": ["text"], "description": "カテゴリ", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "frequency", "dataType": ["int"], "description": "出現頻度", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "trend_score", "dataType": ["number"], "description": "トレンドスコア", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "related_concepts", "dataType": ["text[]"], "description": "関連概念", "vectorizePropertyName": True, "skipVectorization": True},
            ],
            "moduleConfig": {
                # エンベディング設定（Ollama）
                "text2vec-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "dengcao/Qwen3-Embedding-0.6B:F16"
                },
                # ジェネレーティブ設定（Ollama）
                "generative-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "qwen3:0.6b"
                }
            }
        },
        {
            "class": "Citation",
            "description": "引用関係",
            "vectorizer": "text2vec-ollama",  # 引用文脈の検索
            "properties": [
                {"name": "citing_doc_id", "dataType": ["text"], "description": "引用する文書ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "cited_doc_id", "dataType": ["text"], "description": "引用される文書ID", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "citation_context", "dataType": ["text"], "description": "引用文脈", "vectorizePropertyName": True, "skipVectorization": True},
                {"name": "citation_type", "dataType": ["text"], "description": "引用タイプ", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "confidence_score", "dataType": ["number"], "description": "信頼度スコア", "vectorizePropertyName": False, "skipVectorization": True},
                {"name": "created_at", "dataType": ["date"], "description": "作成日時", "vectorizePropertyName": False, "skipVectorization": True},
            ],
            "moduleConfig": {
                # エンベディング設定（Ollama）
                "text2vec-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "dengcao/Qwen3-Embedding-0.6B:F16"
                },
                # ジェネレーティブ設定（Ollama）
                "generative-ollama": {
                    "apiEndpoint": "http://localhost:11434",
                    "model": "qwen3:0.6b"
                }
            }
        }
    ]
}

client = weaviate.connect_to_local()
client.collections.delete_all()  # 既存削除
for class_def in WEAVIATE_SCHEMA["classes"]:
            print(f"クラス '{class_def['class']}' を作成中...")
            client.collections.create_from_dict(class_def)

print("Weaviateのスキーマを作成しました。")



# #














# # Weaviate + Ollama セットアップ用Docker Compose
# WEAVIATE_DOCKER_COMPOSE = """
# version: '3.4'
# services:
#   weaviate:
#     command:
#     - --host
#     - 0.0.0.0
#     - --port
#     - '8080'
#     - --scheme
#     - http
#     image: cr.weaviate.io/semitechnologies/weaviate:1.25.0
#     ports:
#     - "8080:8080"
#     - "50051:50051"
#     restart: on-failure:0
#     environment:
#       QUERY_DEFAULTS_LIMIT: 25
#       AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
#       PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
#       DEFAULT_VECTORIZER_MODULE: 'text2vec-ollama'
#       ENABLE_MODULES: 'text2vec-ollama,generative-ollama'
#       CLUSTER_HOSTNAME: 'node1'
#       # Ollama設定
#       TEXT2VEC_OLLAMA_API_ENDPOINT: 'http://host.docker.internal:11434'
#       GENERATIVE_OLLAMA_API_ENDPOINT: 'http://host.docker.internal:11434'
#     volumes:
#     - weaviate_data:/var/lib/weaviate
# volumes:
#   weaviate_data:
# """

# # エンベディング設定の説明
# """
# 🎯 エンベディング設定方針:

# Document クラス:
# ✅ title, abstract, keywords, research_fields → セマンティック検索
# ❌ IDs, dates, counts, system fields → 構造化検索

# Chunk クラス:
# ✅ content, section_title, entities, key_phrases → 内容検索
# ❌ IDs, positions, scores, system fields → メタデータ検索

# Author クラス:
# ✅ name, affiliations, research_interests → 専門性検索
# ❌ IDs, metrics, contact info → 構造化検索

# Concept クラス:
# ✅ name, description, synonyms, related_concepts → 概念検索
# ❌ IDs, frequencies, categories → 統計的検索

# Citation クラス:
# ✅ citation_context → 引用文脈の検索
# ❌ IDs, types, scores → 関係性データ検索

# 💡 利点:
# 1. LlamaIndexとの併用可能（LlamaIndexが独自ベクトル管理、WeaviateがDBとメタデータ検索）
# 2. 処理効率化（重要プロパティのみベクトル化）
# 3. 多層検索（ベクトル + 構造化フィルタ）
# 4. コスト最適化（Ollama処理時間短縮）
# """

# # 使用例
# def setup_weaviate_with_ollama():
#     """
#     完全なWeaviate + Ollama + LlamaIndex環境の設定
#     """
#     import weaviate
    
#     # Weaviateクライアント
#     client = weaviate.Client("http://localhost:8080")
    
#     # スキーマ作成
#     try:
#         client.schema.delete_all()  # 既存削除
#         client.schema.create(WEAVIATE_SCHEMA)
#         print("✅ All schemas created successfully with Ollama Qwen3!")
        
#         # スキーマ確認
#         schema = client.schema.get()
#         for cls in schema['classes']:
#             print(f"📝 Class: {cls['class']}")
#             vectorized_props = [p['name'] for p in cls['properties'] 
#                               if p.get('vectorizePropertyName', True)]
#             print(f"   🔍 Vectorized properties: {vectorized_props}")
            
#     except Exception as e:
#         print(f"❌ Error: {e}")
    
#     return client

# # 検索例
# def advanced_search_examples(client):
#     """
#     高度な検索例
#     """
    
#     # 1. Document: ハイブリッド検索（ベクトル + フィルタ）
#     results = (
#         client.query
#         .get("Document", ["title", "abstract", "publication_date"])
#         .with_near_text({"concepts": ["transformer neural network"]})
#         .with_where({
#             "path": ["publication_date"],
#             "operator": "GreaterThan", 
#             "valueDate": "2020-01-01T00:00:00Z"
#         })
#         .with_generate(single_prompt="この論文の革新性を日本語で説明して")
#         .with_limit(5)
#         .do()
#     )
    
#     # 2. Chunk: 詳細内容検索
#     chunk_results = (
#         client.query
#         .get("Chunk", ["content", "section_title", "importance_score"])
#         .with_near_text({"concepts": ["attention mechanism implementation"]})
#         .with_where({
#             "path": ["importance_score"],
#             "operator": "GreaterThan",
#             "valueNumber": 0.7
#         })
#         .with_limit(10)
#         .do()
#     )
    
#     # 3. Author: 研究者検索
#     author_results = (
#         client.query
#         .get("Author", ["name", "research_interests", "affiliations"])
#         .with_near_text({"concepts": ["deep learning computer vision"]})
#         .with_generate(single_prompt="この研究者の専門分野を要約して")
#         .do()
#     )
    
#     return results, chunk_results, author_results

# if __name__ == "__main__":
#     # Ollama起動確認
#     print("🚀 Ollamaが起動していることを確認してください:")
#     print("   ollama serve")
#     print("   ollama pull qwen2.5:latest")
#     print()
    
#     # セットアップ実行
#     client = setup_weaviate_with_ollama()
    
#     # 検索テスト（データがある場合）
#     # results = advanced_search_examples(client)





# """
# 文献ベクトルデータベース設計
# LlamaIndex + Weaviate を使用した学術文献管理システム
# """

# from typing import List, Dict, Optional, Any, Union
# from datetime import datetime
# from enum import Enum
# import uuid
# import logging
# from dataclasses import dataclass, field
# from pathlib import Path
# import hashlib
# import json

# # ロギング設定
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class ChunkType(Enum):
#     """チャンクの種類"""
#     TITLE = "title"
#     ABSTRACT = "abstract"
#     INTRODUCTION = "introduction"
#     METHODOLOGY = "methodology"
#     RESULTS = "results"
#     DISCUSSION = "discussion"
#     CONCLUSION = "conclusion"
#     REFERENCE = "reference"
#     FIGURE_CAPTION = "figure_caption"
#     TABLE_CAPTION = "table_caption"
#     FULL_TEXT = "full_text"

# class DocumentType(Enum):
#     """文書の種類"""
#     JOURNAL_ARTICLE = "journal_article"
#     CONFERENCE_PAPER = "conference_paper"
#     BOOK_CHAPTER = "book_chapter"
#     THESIS = "thesis"
#     PREPRINT = "preprint"
#     PATENT = "patent"
#     REPORT = "report"

# class ProcessingStatus(Enum):
#     """処理状況"""
#     PENDING = "pending"
#     PROCESSING = "processing"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     NEEDS_REVIEW = "needs_review"

# class StorageType(Enum):
#     """全文保存方式"""
#     EMBEDDED = "embedded"
#     EXTERNAL = "external"
#     REFERENCE = "reference"

# # Weaviate スキーマ設計
# WEAVIATE_SCHEMA = {
#     "classes": [
#         {
#             "class": "Document",
#             "description": "学術文献のメタデータ",
#             "vectorizer": "none",  # LlamaIndexで管理
#             "properties": [
#                 # 基本メタデータ
#                 {"name": "document_id", "dataType": ["text"], "description": "文書の一意識別子"},
#                 {"name": "title", "dataType": ["text"], "description": "文献タイトル"},
#                 {"name": "abstract", "dataType": ["text"], "description": "要約"},
#                 {"name": "authors", "dataType": ["text[]"], "description": "著者リスト"},
#                 {"name": "affiliations", "dataType": ["text[]"], "description": "所属機関"},
#                 {"name": "publication_date", "dataType": ["date"], "description": "発行日"},
#                 {"name": "journal_name", "dataType": ["text"], "description": "雑誌名"},
#                 {"name": "volume", "dataType": ["text"], "description": "巻号"},
#                 {"name": "issue", "dataType": ["text"], "description": "号"},
#                 {"name": "pages", "dataType": ["text"], "description": "ページ範囲"},
#                 {"name": "doi", "dataType": ["text"], "description": "DOI"},
#                 # {"name": "pmid", "dataType": ["text"], "description": "PubMed ID"},
#                 {"name": "arxiv_id", "dataType": ["text"], "description": "arXiv ID"},
                
#                 # 全文データ管理
#                 {"name": "has_full_text", "dataType": ["boolean"], "description": "全文データの有無"},
#                 {"name": "full_text_storage_type", "dataType": ["text"], "description": "全文保存方式"},
#                 {"name": "full_text_url", "dataType": ["text"], "description": "全文アクセスURL"},
#                 {"name": "full_text_hash", "dataType": ["text"], "description": "全文のハッシュ値"},
#                 {"name": "license_type", "dataType": ["text"], "description": "ライセンス種別"},
#                 {"name": "access_permission", "dataType": ["text"], "description": "アクセス権限"},
                
#                 # 分類情報
#                 # {"name": "document_type", "dataType": ["text"], "description": "文書種別"},
#                 # {"name": "subject_categories", "dataType": ["text[]"], "description": "主題分類"},
#                 {"name": "keywords", "dataType": ["text[]"], "description": "キーワード"},
#                 {"name": "research_fields", "dataType": ["text[]"], "description": "研究分野"},
                
#                 # # 品質・重要度指標
#                 # {"name": "citation_count", "dataType": ["int"], "description": "被引用数"},
#                 # {"name": "impact_factor", "dataType": ["number"], "description": "インパクトファクター"},
#                 # {"name": "h_index", "dataType": ["number"], "description": "著者のh-index"},
#                 # {"name": "quality_score", "dataType": ["number"], "description": "品質スコア"},
                
#                 # システム管理
#                 {"name": "created_at", "dataType": ["date"], "description": "登録日時"},
#                 {"name": "updated_at", "dataType": ["date"], "description": "更新日時"},
#                 {"name": "source_url", "dataType": ["text"], "description": "元データのURL"},
#                 {"name": "file_path", "dataType": ["text"], "description": "ファイルパス"},
#                 # {"name": "processing_status", "dataType": ["text"], "description": "処理状況"},
                
#                 # 言語・地域情報
#                 {"name": "language", "dataType": ["text"], "description": "言語"},
#                 {"name": "country", "dataType": ["text"], "description": "発行国"},
                
#                 # 統計情報
#                 {"name": "word_count", "dataType": ["int"], "description": "単語数"},
#                 {"name": "page_count", "dataType": ["int"], "description": "ページ数"},
#                 {"name": "reference_count", "dataType": ["int"], "description": "参考文献数"},
#                 {"name": "figure_count", "dataType": ["int"], "description": "図表数"},
#             ],
#             "moduleConfig": {
#                 "generative-openai": {
#                     "model": "gpt-4"
#                 }
#             }
#         },
#         {
#             "class": "Chunk",
#             "description": "文献の分割されたテキストチャンク",
#             "vectorizer": "none",  # LlamaIndexで管理
#             "properties": [
#                 # チャンク基本情報
#                 {"name": "chunk_id", "dataType": ["text"], "description": "チャンクの一意識別子"},
#                 {"name": "document_id", "dataType": ["text"], "description": "親文書ID"},
#                 {"name": "chunk_type", "dataType": ["text"], "description": "チャンク種別"},
#                 {"name": "content", "dataType": ["text"], "description": "チャンク内容"},
#                 {"name": "chunk_index", "dataType": ["int"], "description": "文書内での順序"},
#                 {"name": "section_title", "dataType": ["text"], "description": "セクションタイトル"},
                
#                 # 位置情報
#                 {"name": "start_char", "dataType": ["int"], "description": "開始文字位置"},
#                 {"name": "end_char", "dataType": ["int"], "description": "終了文字位置"},
#                 {"name": "page_number", "dataType": ["int"], "description": "ページ番号"},
                
#                 # 内容分析
#                 {"name": "word_count", "dataType": ["int"], "description": "単語数"},
#                 {"name": "sentence_count", "dataType": ["int"], "description": "文数"},
#                 {"name": "entities", "dataType": ["text[]"], "description": "抽出された固有表現"},
#                 {"name": "key_phrases", "dataType": ["text[]"], "description": "重要フレーズ"},
                
#                 # 品質指標
#                 {"name": "importance_score", "dataType": ["number"], "description": "重要度スコア"},
#                 {"name": "readability_score", "dataType": ["number"], "description": "可読性スコア"},
#                 {"name": "semantic_density", "dataType": ["number"], "description": "意味密度"},
                
#                 # システム管理
#                 {"name": "created_at", "dataType": ["date"], "description": "作成日時"},
#                 {"name": "embedding_model", "dataType": ["text"], "description": "使用した埋め込みモデル"},
#                 {"name": "processing_version", "dataType": ["text"], "description": "処理バージョン"},
#             ]
#         },
#         {
#             "class": "Author",
#             "description": "著者情報",
#             "vectorizer": "none",
#             "properties": [
#                 {"name": "author_id", "dataType": ["text"], "description": "著者ID"},
#                 {"name": "name", "dataType": ["text"], "description": "著者名"},
#                 {"name": "normalized_name", "dataType": ["text"], "description": "正規化された著者名"},
#                 {"name": "affiliations", "dataType": ["text[]"], "description": "所属機関履歴"},
#                 {"name": "orcid", "dataType": ["text"], "description": "ORCID ID"},
#                 {"name": "research_interests", "dataType": ["text[]"], "description": "研究興味"},
#                 {"name": "h_index", "dataType": ["number"], "description": "h-index"},
#                 {"name": "citation_count", "dataType": ["int"], "description": "総被引用数"},
#                 {"name": "publication_count", "dataType": ["int"], "description": "出版数"},
#                 {"name": "email", "dataType": ["text"], "description": "メールアドレス"},
#                 {"name": "homepage", "dataType": ["text"], "description": "ホームページURL"},
#             ]
#         },
#         {
#             "class": "Concept",
#             "description": "研究概念・トピック",
#             "vectorizer": "none",
#             "properties": [
#                 {"name": "concept_id", "dataType": ["text"], "description": "概念ID"},
#                 {"name": "name", "dataType": ["text"], "description": "概念名"},
#                 {"name": "description", "dataType": ["text"], "description": "概念の説明"},
#                 {"name": "synonyms", "dataType": ["text[]"], "description": "同義語"},
#                 {"name": "category", "dataType": ["text"], "description": "カテゴリ"},
#                 {"name": "frequency", "dataType": ["int"], "description": "出現頻度"},
#                 {"name": "trend_score", "dataType": ["number"], "description": "トレンドスコア"},
#                 {"name": "related_concepts", "dataType": ["text[]"], "description": "関連概念"},
#             ]
#         },
#         {
#             "class": "Citation",
#             "description": "引用関係",
#             "vectorizer": "none",
#             "properties": [
#                 {"name": "citing_doc_id", "dataType": ["text"], "description": "引用する文書ID"},
#                 {"name": "cited_doc_id", "dataType": ["text"], "description": "引用される文書ID"},
#                 {"name": "citation_context", "dataType": ["text"], "description": "引用文脈"},
#                 {"name": "citation_type", "dataType": ["text"], "description": "引用タイプ"},
#                 {"name": "confidence_score", "dataType": ["number"], "description": "信頼度スコア"},
#                 {"name": "created_at", "dataType": ["date"], "description": "作成日時"},
#             ]
#         }
#     ]
# }

# @dataclass
# class LiteratureDocument:
#     """LlamaIndexで使用する文献文書クラス"""
#     document_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     title: str = ""
#     abstract: str = ""
#     full_text: str = ""
#     authors: List[str] = field(default_factory=list)
#     publication_date: Optional[datetime] = None
#     doi: Optional[str] = None
#     document_type: DocumentType = DocumentType.JOURNAL_ARTICLE
#     metadata: Dict[str, Any] = field(default_factory=dict)
#     chunks: List[Dict] = field(default_factory=list)
    
#     def __post_init__(self):
#         """初期化後の処理"""
#         if not self.metadata.get('created_at'):
#             self.metadata['created_at'] = datetime.now().isoformat()
    
#     def to_llamaindex_document(self):
#         """LlamaIndexのDocumentオブジェクトに変換"""
#         try:
#             from llama_index.core import Document
            
#             # メタデータの準備
#             metadata = {
#                 "document_id": self.document_id,
#                 "title": self.title,
#                 "abstract": self.abstract,
#                 "authors": self.authors,
#                 "publication_date": self.publication_date.isoformat() if self.publication_date else None,
#                 "doi": self.doi,
#                 "document_type": self.document_type.value,
#                 **self.metadata
#             }
            
#             # 全文が空の場合は抄録を使用
#             text_content = self.full_text or self.abstract or self.title
            
#             return Document(
#                 text=text_content,
#                 doc_id=self.document_id,
#                 metadata=metadata
#             )
#         except ImportError:
#             logger.error("LlamaIndex not installed. Please install llama-index.")
#             raise
    
#     def generate_hash(self) -> str:
#         """文書のハッシュ値を生成"""
#         content = f"{self.title}{self.abstract}{self.full_text}"
#         return hashlib.sha256(content.encode()).hexdigest()
    
#     def validate(self) -> bool:
#         """文書の妥当性を検証"""
#         if not self.title:
#             logger.warning(f"Document {self.document_id} has no title")
#             return False
        
#         if not self.abstract and not self.full_text:
#             logger.warning(f"Document {self.document_id} has no content")
#             return False
        
#         return True

# # 設定クラス
# @dataclass
# class IndexConfig:
#     """インデックス設定"""
#     embedding_model: str = "text-embedding-3-large"
#     chunk_size: int = 512
#     chunk_overlap: int = 50
#     similarity_top_k: int = 10
#     similarity_threshold: float = 0.7
#     rerank_top_n: int = 5
#     batch_size: int = 100
    
#     def to_dict(self) -> Dict[str, Any]:
#         """辞書形式に変換"""
#         return {
#             "embedding_model": self.embedding_model,
#             "chunk_size": self.chunk_size,
#             "chunk_overlap": self.chunk_overlap,
#             "similarity_top_k": self.similarity_top_k,
#             "similarity_threshold": self.similarity_threshold,
#             "rerank_top_n": self.rerank_top_n,
#             "batch_size": self.batch_size
#         }

# @dataclass
# class SearchConfig:
#     """検索設定"""
#     hybrid_search: bool = True
#     filters: Dict[str, Any] = field(default_factory=dict)
#     boost_fields: Dict[str, float] = field(default_factory=dict)
    
#     def __post_init__(self):
#         """デフォルト値の設定"""
#         if not self.filters:
#             self.filters = {
#                 "publication_date": {"gte": "2020-01-01"},
#                 "document_type": ["journal_article", "conference_paper"],
#                 "citation_count": {"gte": 10}
#             }
        
#         if not self.boost_fields:
#             self.boost_fields = {
#                 "title": 2.0,
#                 "abstract": 1.5,
#                 "keywords": 1.2
#             }

# # 全文データ管理クラス
# class FullTextManager:
#     """全文データへのアクセスを管理"""
    
#     def __init__(self, storage_config: Dict[str, Any]):
#         self.storage_config = storage_config
#         self.cache = {}  # シンプルなキャッシュ
        
#     def get_full_text(self, document_id: str) -> Optional[str]:
#         """文書IDから全文を取得"""
#         try:
#             # キャッシュから取得を試行
#             if document_id in self.cache:
#                 return self.cache[document_id]
                
#             doc_meta = self.get_document_metadata(document_id)
#             if not doc_meta:
#                 return None
                
#             storage_type = doc_meta.get("full_text_storage_type")
            
#             if storage_type == StorageType.EMBEDDED.value:
#                 text = self._get_embedded_text(document_id)
#             elif storage_type == StorageType.EXTERNAL.value:
#                 text = self._get_external_text(doc_meta.get("full_text_url"))
#             elif storage_type == StorageType.REFERENCE.value:
#                 text = self._get_reference_text(doc_meta.get("full_text_url"))
#             else:
#                 logger.warning(f"Unknown storage type: {storage_type}")
#                 return None
            
#             # キャッシュに保存
#             if text:
#                 self.cache[document_id] = text
                
#             return text
            
#         except Exception as e:
#             logger.error(f"Error getting full text for document {document_id}: {e}")
#             return None
    
#     def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
#         """文書メタデータを取得（実装必要）"""
#         # 実際の実装では、Weaviateからメタデータを取得
#         pass
    
#     def get_document_chunks(self, document_id: str) -> List[Dict]:
#         """文書のチャンクを取得（実装必要）"""
#         # 実際の実装では、Weaviateからチャンクを取得
#         pass
    
#     def _get_embedded_text(self, document_id: str) -> Optional[str]:
#         """埋め込み保存された全文を取得"""
#         try:
#             chunks = self.get_document_chunks(document_id)
#             if not chunks:
#                 return None
                
#             # チャンクを順序でソートして結合
#             sorted_chunks = sorted(chunks, key=lambda x: x.get("chunk_index", 0))
#             return "".join([chunk.get("content", "") for chunk in sorted_chunks])
            
#         except Exception as e:
#             logger.error(f"Error getting embedded text: {e}")
#             return None
    
#     def _get_external_text(self, url: str) -> Optional[str]:
#         """外部ストレージから全文を取得"""
#         try:
#             # S3, GCS等から取得の実装
#             # 実際の実装では、boto3やgoogle-cloud-storageを使用
#             logger.info(f"Fetching text from external storage: {url}")
#             return None  # 実装必要
#         except Exception as e:
#             logger.error(f"Error getting external text from {url}: {e}")
#             return None
    
#     def _get_reference_text(self, url: str) -> Optional[str]:
#         """参照URLから全文を取得"""
#         try:
#             # 元サイトやAPIから取得の実装
#             # 実際の実装では、requests等を使用
#             logger.info(f"Fetching text from reference URL: {url}")
#             return None  # 実装必要
#         except Exception as e:
#             logger.error(f"Error getting reference text from {url}: {e}")
#             return None

# # ベクトルデータベースクラス
# class LiteratureVectorDB:
#     """文献ベクトルデータベースの管理クラス"""
    
#     def __init__(self, weaviate_client, config: IndexConfig):
#         self.client = weaviate_client
#         self.config = config
#         self.full_text_manager = FullTextManager({})
        
#     def create_schema(self):
#         """Weaviateスキーマを作成"""
#         try:
#             # 既存のスキーマを削除（開発環境のみ）
#             existing_classes = self.client.schema.get()["classes"]
#             for cls in existing_classes:
#                 if cls["class"] in [c["class"] for c in WEAVIATE_SCHEMA["classes"]]:
#                     self.client.schema.delete_class(cls["class"])
            
#             # 新しいスキーマを作成
#             for class_config in WEAVIATE_SCHEMA["classes"]:
#                 self.client.schema.create_class(class_config)
                
#             logger.info("Schema created successfully")
            
#         except Exception as e:
#             logger.error(f"Error creating schema: {e}")
#             raise
    
#     def create_index(self, documents: List[LiteratureDocument]):
#         """文献インデックスを作成"""
#         try:
#             from llama_index.core import VectorStoreIndex, StorageContext
#             from llama_index.vector_stores.weaviate import WeaviateVectorStore
            
#             # ベクトルストア設定
#             vector_store = WeaviateVectorStore(
#                 weaviate_client=self.client,
#                 index_name="Document",
#                 text_key="content"
#             )
            
#             # ストレージコンテキスト
#             storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
#             # 文書の妥当性チェック
#             valid_documents = [doc for doc in documents if doc.validate()]
#             logger.info(f"Processing {len(valid_documents)} valid documents")
            
#             # LlamaIndexドキュメントに変換
#             llama_docs = [doc.to_llamaindex_document() for doc in valid_documents]
            
#             # インデックス作成
#             index = VectorStoreIndex.from_documents(
#                 documents=llama_docs,
#                 storage_context=storage_context,
#                 embed_model=self.config.embedding_model,
#                 show_progress=True
#             )
            
#             logger.info("Index created successfully")
#             return index
            
#         except Exception as e:
#             logger.error(f"Error creating index: {e}")
#             raise
    
#     def search_literature(self, index, query: str, search_config: SearchConfig):
#         """文献検索"""
#         try:
#             retriever = index.as_retriever(
#                 similarity_top_k=self.config.similarity_top_k,
#                 filters=search_config.filters
#             )
            
#             results = retriever.retrieve(query)
            
#             # 結果の後処理
#             processed_results = []
#             for result in results:
#                 processed_results.append({
#                     "document_id": result.metadata.get("document_id"),
#                     "title": result.metadata.get("title"),
#                     "score": result.score,
#                     "content": result.text,
#                     "metadata": result.metadata
#                 })
            
#             return processed_results
            
#         except Exception as e:
#             logger.error(f"Error searching literature: {e}")
#             return []

# # 使用例
# def create_literature_system():
#     """文献システムの作成例"""
#     try:
#         import weaviate
        
#         # Weaviateクライアント設定
#         client = weaviate.Client(
#             url="http://localhost:8080",
#             additional_headers={"X-OpenAI-Api-Key": "your-api-key"}
#         )
        
#         # 設定
#         config = IndexConfig(
#             embedding_model="text-embedding-3-large",
#             chunk_size=512,
#             chunk_overlap=50
#         )
        
#         # システム初期化
#         system = LiteratureVectorDB(client, config)
#         system.create_schema()
        
#         # サンプル文献作成
#         sample_doc = LiteratureDocument(
#             title="Sample Research Paper",
#             abstract="This is a sample abstract for demonstration purposes.",
#             authors=["John Doe", "Jane Smith"],
#             publication_date=datetime.now(),
#             doi="10.1000/sample.doi"
#         )
        
#         # インデックス作成
#         index = system.create_index([sample_doc])
        
#         # 検索設定
#         search_config = SearchConfig(
#             hybrid_search=True,
#             filters={"document_type": ["journal_article"]}
#         )
        
#         # 検索実行
#         results = system.search_literature(index, "sample query", search_config)
        
#         return system, index, results
        
#     except ImportError:
#         logger.error("Required libraries not installed. Please install weaviate-client and llama-index.")
#         return None, None, None

# # 推奨設定
# RECOMMENDED_STORAGE_CONFIG = {
#     "open_access": StorageType.EMBEDDED.value,
#     "subscription": StorageType.REFERENCE.value,
#     "internal": StorageType.EMBEDDED.value,
#     "large_corpus": StorageType.EXTERNAL.value,
    
#     "chunk_only_mode": True,
#     "abstract_always_embedded": True,
#     "compression": "gzip",
#     "encryption": True,
#     "max_cache_size": 1000,
#     "cache_ttl": 3600,  # 1時間
# }

# # データ更新・同期の設定
# SYNC_CONFIG = {
#     "incremental_update": True,
#     "batch_size": 1000,
#     "parallel_processing": True,
#     "backup_interval": "weekly",
#     "index_rebuild_interval": "monthly",
#     "max_retries": 3,
#     "retry_delay": 5,  # 秒
# }

# if __name__ == "__main__":
#     # システムの作成と実行
#     system, index, results = create_literature_system()
#     if system:
#         logger.info("Literature system created successfully")
#         if results:
#             logger.info(f"Found {len(results)} search results")
#     else:
#         logger.error("Failed to create literature system")