import os
import json
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.tools import Tool 
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain_weaviate import WeaviateVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.tools import Tool

# 環境変数の読み込み
load_dotenv()

# Ollamaの設定
ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')  # 日本語対応の良いモデル
ollama_embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'bge-m3')  # 日本語対応embeddingモデル

# Weaviateの接続設定
weaviate_url = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
weaviate_api_key = os.getenv('WEAVIATE_API_KEY', None)

# Weaviate v4での接続
try:
    if weaviate_api_key:
        client = weaviate.connect_to_local(
            host=weaviate_url.replace('http://', '').replace('https://', ''),
            headers={"X-OpenAI-Api-Key": weaviate_api_key} if weaviate_api_key else None
        )
    else:
        client = weaviate.connect_to_local()
    
    print("Weaviateに接続しました")
except Exception as e:
    print(f"Weaviate接続エラー: {e}")
    exit(1)

# コレクション名
COLLECTION_NAME = "Patent"

# Weaviate v4でのコレクション作成
def create_patent_collection():
    """特許データ用のコレクションを作成"""
    try:
        # 既存のコレクションを確認
        if client.collections.exists(COLLECTION_NAME):
            print(f"コレクション '{COLLECTION_NAME}' は既に存在します")
            return client.collections.get(COLLECTION_NAME)
        
        # 新しいコレクション作成
        collection = client.collections.create(
            name=COLLECTION_NAME,
            properties=[
                Property(name="title", data_type=DataType.TEXT, description="特許のタイトル"),
                Property(name="abstract", data_type=DataType.TEXT, description="特許の概要"),
                Property(name="claims", data_type=DataType.TEXT, description="特許の請求項"),
                Property(name="publication_date", data_type=DataType.DATE, description="公開日"),
                Property(name="application_number", data_type=DataType.TEXT, description="出願番号"),
                Property(name="inventors", data_type=DataType.TEXT_ARRAY, description="発明者リスト"),
                Property(name="assignee", data_type=DataType.TEXT, description="特許権者"),
                Property(name="patent_number", data_type=DataType.TEXT, description="特許番号"),
                Property(name="classification_codes", data_type=DataType.TEXT_ARRAY, description="特許分類コード"),
                Property(name="content", data_type=DataType.TEXT, description="特許の本文内容"),
                Property(name="chunk_id", data_type=DataType.INT, description="チャンクID"),
                Property(name="total_chunks", data_type=DataType.INT, description="総チャンク数")
            ],
            # ベクトライザーを無効化（外部embeddingを使用）
            vectorizer_config=Configure.Vectorizer.none()
        )
        
        print(f"コレクション '{COLLECTION_NAME}' を作成しました")
        return collection
        
    except Exception as e:
        print(f"コレクション作成エラー: {e}")
        return None

# コレクションを取得または作成
patent_collection = create_patent_collection()
if not patent_collection:
    print("コレクションの作成に失敗しました")
    exit(1)

# 日本語対応embeddingの設定
embeddings = OllamaEmbeddings(
    base_url=ollama_base_url,
    model=ollama_embedding_model
)

# LangChain用のWeaviateベクトルストアを設定
vectorstore = WeaviateVectorStore(
    client=client,
    index_name=COLLECTION_NAME,
    text_key="content",
    embedding=embeddings
)

# LLMの設定（日本語プロンプト対応）
llm = OllamaLLM(
    base_url=ollama_base_url,
    model=ollama_model,
    temperature=0.1
)

# 特許データ読み込み関数
def load_patent_data(file_path):
    """JSONファイルから特許データを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                print("データ形式が不正です")
                return []
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"JSONファイルの形式が不正です: {file_path}")
        return []
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return []

# 特許データをWeaviateにインポートする関数（Weaviate v4対応）
def import_patents_to_weaviate(patents):
    """特許データをWeaviateにインポートする"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "。", "．", "!", "?", "！", "？", " ", ""]
    )
    
    imported_count = 0
    
    try:
        with patent_collection.batch.dynamic() as batch:
            for patent in patents:
                try:
                    # 特許の主要部分をテキストとして結合
                    full_text = ""
                    if patent.get('title'):
                        full_text += f"タイトル: {patent['title']}\n\n"
                    if patent.get('abstract'):
                        full_text += f"概要: {patent['abstract']}\n\n"
                    if patent.get('claims'):
                        full_text += f"請求項: {patent['claims']}\n\n"
                    
                    # 追加情報も含める
                    if patent.get('inventors'):
                        inventors = patent['inventors'] if isinstance(patent['inventors'], list) else [patent['inventors']]
                        full_text += f"発明者: {', '.join(inventors)}\n"
                    if patent.get('assignee'):
                        full_text += f"特許権者: {patent['assignee']}\n"
                    if patent.get('classification_codes'):
                        codes = patent['classification_codes'] if isinstance(patent['classification_codes'], list) else [patent['classification_codes']]
                        full_text += f"分類コード: {', '.join(codes)}\n"
                    
                    if not full_text.strip():
                        print(f"空のテキストデータをスキップしました: {patent.get('patent_number', 'Unknown')}")
                        continue
                    
                    # テキストを分割
                    texts = text_splitter.split_text(full_text)
                    
                    # 分割したテキストをバッチ追加
                    for i, text in enumerate(texts):
                        # ベクトル化
                        vector = embeddings.embed_query(text)
                        
                        # プロパティを準備
                        properties = {
                            "content": text,
                            "title": patent.get('title', ''),
                            "abstract": patent.get('abstract', ''),
                            "claims": patent.get('claims', ''),
                            "application_number": patent.get('application_number', ''),
                            "assignee": patent.get('assignee', ''),
                            "patent_number": patent.get('patent_number', ''),
                            "chunk_id": i,
                            "total_chunks": len(texts)
                        }
                        
                        # 配列型のプロパティを処理
                        if patent.get('inventors'):
                            properties["inventors"] = patent['inventors'] if isinstance(patent['inventors'], list) else [patent['inventors']]
                        
                        if patent.get('classification_codes'):
                            properties["classification_codes"] = patent['classification_codes'] if isinstance(patent['classification_codes'], list) else [patent['classification_codes']]
                        
                        # 日付型のプロパティを処理
                        if patent.get('publication_date'):
                            properties["publication_date"] = patent['publication_date']
                        
                        # バッチにオブジェクトを追加
                        batch.add_object(
                            properties=properties,
                            vector=vector
                        )
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"特許データのインポートエラー: {patent.get('patent_number', 'Unknown')} - {e}")
                    continue
        
        print(f"{imported_count}件の特許データをインポートしました")
        
    except Exception as e:
        print(f"バッチインポートエラー: {e}")

# 特許検索ツール（改良版）
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

patent_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

def patent_search_func(query):
    """特許検索機能の改良版"""
    try:
        result = patent_qa.invoke({"query": query})
        answer = result['result']
        sources = result['source_documents']
        
        # ソース情報を追加
        if sources:
            answer += "\n\n【参照元特許情報】\n"
            for i, source in enumerate(sources[:3], 1):
                metadata = source.metadata
                answer += f"{i}. 特許番号: {metadata.get('patent_number', 'N/A')}\n"
                answer += f"   タイトル: {metadata.get('title', 'N/A')}\n"
                answer += f"   特許権者: {metadata.get('assignee', 'N/A')}\n\n"
        
        return answer
    except Exception as e:
        return f"検索エラーが発生しました: {e}"

patent_search_tool = Tool(
    name="PatentSearch",
    func=patent_search_func,
    description="特許情報を検索するツール。技術トピック、発明者、特許番号、企業名などで検索できます。日本語で質問してください。"
)

# 特許分析ツール（改良版）
def analyze_patent_trends(query):
    """特許のトレンドを分析する"""
    try:
        docs = retriever.invoke(query)
        
        if not docs:
            return f"'{query}'に関連する特許情報が見つかりませんでした。"
        
        # 分析用のプロンプト（日本語対応）
        analysis_prompt = f"""以下の特許情報に基づいて、「{query}」に関する技術トレンドを日本語で分析してください。

分析の観点：
1. 重要な技術パターンや革新的な技術
2. 主要な企業や発明者
3. この分野の技術発展の方向性
4. 市場への影響や将来性

特許情報:
{[doc.page_content for doc in docs[:3]]}

分析結果を日本語で詳しく説明してください。"""
        
        return llm.invoke(analysis_prompt)
    except Exception as e:
        return f"分析エラーが発生しました: {e}"

patent_analysis_tool = Tool(
    name="PatentAnalysis",
    func=analyze_patent_trends,
    description="特定の技術分野や企業に関する特許のトレンドを分析するツール。日本語で技術分野や企業名を入力してください。"
)

# 類似特許検索ツール（改良版）
def find_similar_patents(patent_description):
    """類似特許を検索する"""
    try:
        docs = retriever.invoke(patent_description)
        
        if not docs:
            return f"'{patent_description}'に類似する特許情報が見つかりませんでした。"
        
        # 結果整形用のプロンプト（日本語対応）
        format_prompt = f"""以下の特許情報から、入力された発明アイデア「{patent_description}」に類似する特許を特定し、日本語で簡潔にまとめてください。

各特許について以下の情報を含めてください：
- 特許番号とタイトル
- 概要
- 元のアイデアとの類似点と相違点
- 特許権者

特許情報:
{[doc.page_content for doc in docs[:3]]}

結果を日本語で整理して説明してください。"""
        
        return llm.invoke(format_prompt)
    except Exception as e:
        return f"類似特許検索エラーが発生しました: {e}"

similar_patent_tool = Tool(
    name="SimilarPatentFinder",
    func=find_similar_patents,
    description="入力された発明アイデアや技術説明に類似する既存特許を検索するツール。日本語で発明アイデアを入力してください。"
)

# 特許出願アドバイスツール（改良版）
def patent_filing_advice(invention_description):
    """特許出願のアドバイスを提供する"""
    try:
        docs = retriever.invoke(invention_description)
        
        advice_prompt = f"""以下の発明アイデア「{invention_description}」と関連する既存特許情報に基づいて、特許出願に関するアドバイスを日本語で提供してください。

アドバイスに含める内容：
1. 既存特許との差別化のポイント
2. 強調すべき革新的側面
3. 出願戦略の提案
4. 注意すべき先行技術
5. 特許性の評価

関連特許情報:
{[doc.page_content for doc in docs[:3]]}

実用的なアドバイスを日本語で提供してください。"""
        
        return llm.invoke(advice_prompt)
    except Exception as e:
        return f"アドバイス生成エラーが発生しました: {e}"

patent_advice_tool = Tool(
    name="PatentAdvice",
    func=patent_filing_advice,
    description="特許出願戦略についてアドバイスを提供するツール。既存特許との差別化方法を提案します。日本語で発明内容を入力してください。"
)

# ツールリスト
tools = [
    patent_search_tool,
    patent_analysis_tool,
    similar_patent_tool,
    patent_advice_tool
]

# ReAct プロンプトテンプレート（日本語対応）
react_prompt = PromptTemplate.from_template("""
あなたは特許調査の専門家です。以下のツールを使用して、ユーザーの質問に日本語で回答してください。

利用可能なツール:
{tools}

ツールの説明:
{tool_names}

次の形式で思考と行動を行ってください:

質問: 回答すべき入力質問
思考: 何をすべきか考える
行動: 実行するアクション。[{tool_names}]の中から選択
行動の入力: アクションへの入力
観察: アクションの結果
... (この思考/行動/行動の入力/観察は必要に応じて繰り返す)
思考: 最終的な答えが分かった
最終回答: ユーザーへの最終的な回答

質問: {input}
{agent_scratchpad}
""")

# エージェントの作成（LangChain v4対応）
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt
)

# エージェントエグゼキュータの作成
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

# ヘルプ表示関数
def show_help():
    """ヘルプ情報を表示する"""
    help_text = """
=== 特許調査エージェント（Weaviate v4対応版）===

【基本コマンド】
- import [ファイルパス] : JSONファイルから特許データをインポート
- help : このヘルプを表示
- exit : エージェントを終了

【使用可能なツール】
1. PatentSearch : 特許情報を検索
   例: "人工知能に関する特許を検索して"
   
2. PatentAnalysis : 特許トレンドを分析  
   例: "機械学習分野の特許トレンドを分析して"
   
3. SimilarPatentFinder : 類似特許を検索
   例: "画像認識技術を使った顔認証システムに類似する特許を探して"
   
4. PatentAdvice : 特許出願アドバイス
   例: "音声認識AIの特許出願について助言して"

【使用例】
> トヨタの自動運転に関する特許を検索して
> 2020年以降のAI関連特許のトレンドを分析して
> ブロックチェーンを使った決済システムに類似する特許はある？

日本語で自然に質問してください。
"""
    print(help_text)

# メイン関数
def main():
    print("=== 特許調査エージェント（Weaviate v4 + LangChain v4対応版）===")
    print("起動しました。")
    print("'help'でヘルプを表示、'exit'で終了します。")
    print("質問は日本語で入力してください。")
    
    try:
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    print("エージェントを終了します。")
                    break
                
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                
                elif user_input.lower().startswith('import '):
                    file_path = user_input[7:].strip()
                    if not file_path:
                        print("ファイルパスを指定してください。例: import patents.json")
                        continue
                        
                    print(f"'{file_path}' からデータをインポートします...")
                    patents = load_patent_data(file_path)
                    if patents:
                        import_patents_to_weaviate(patents)
                    else:
                        print("インポートするデータがありませんでした。")
                
                else:
                    print("処理中...")
                    result = agent_executor.invoke({"input": user_input})
                    print("\n【回答】")
                    print(result['output'])
                    
            except KeyboardInterrupt:
                print("\n\nエージェントを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                print("もう一度試してください。")
    
    finally:
        # Weaviate接続を閉じる
        try:
            client.close()
            print("Weaviate接続を閉じました。")
        except:
            pass

if __name__ == "__main__":
    main()