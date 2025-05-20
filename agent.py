import os
import json
import weaviate
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.vectorstores import Weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Ollamaの設定
ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')  # デフォルトはllama3

# Weaviateの接続設定
weaviate_url = os.getenv('WEAVIATE_URL', 'http://localhost:8080')  # デフォルトはローカルホスト
weaviate_api_key = os.getenv('WEAVIATE_API_KEY', None)  # オプション

# Weaviateに接続
client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=weaviate_api_key) if weaviate_api_key else None,
)

# Weaviateのスキーマ定義（特許データ用）
class_obj = {
    "class": "Patent",
    "vectorizer": "text2vec-contextionary",  # Weaviateのデフォルトベクトライザーを使用
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "特許のタイトル"
        },
        {
            "name": "abstract",
            "dataType": ["text"],
            "description": "特許の概要"
        },
        {
            "name": "claims",
            "dataType": ["text"],
            "description": "特許の請求項"
        },
        {
            "name": "publication_date",
            "dataType": ["date"],
            "description": "公開日"
        },
        {
            "name": "application_number",
            "dataType": ["string"],
            "description": "出願番号"
        },
        {
            "name": "inventors",
            "dataType": ["string[]"],
            "description": "発明者リスト"
        },
        {
            "name": "assignee",
            "dataType": ["string"],
            "description": "特許権者"
        },
        {
            "name": "patent_number",
            "dataType": ["string"],
            "description": "特許番号"
        },
        {
            "name": "classification_codes",
            "dataType": ["string[]"],
            "description": "特許分類コード"
        }
    ]
}

# Weaviateにスキーマが存在しない場合は作成
if not client.schema.exists("Patent"):
    client.schema.create_class(class_obj)
    print("Patentクラスを作成しました")
else:
    print("Patentクラスは既に存在します")

# LangChain用のWeaviateラッパーを設定
embeddings = OllamaEmbeddings(
    base_url=ollama_base_url,
    model=ollama_model
)
vectorstore = Weaviate(client, "Patent", "text", embeddings)

# LLMの設定
llm = Ollama(
    base_url=ollama_base_url,
    model=ollama_model,
    temperature=0.1
)

# 特許データ読み込み関数
def load_patent_data(file_path):
    """JSONファイルから特許データを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return []

# 特許データをWeaviateにインポートする関数
def import_patents_to_weaviate(patents):
    """特許データをWeaviateにインポートする"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    for patent in patents:
        # 特許の主要部分をテキストとして結合
        full_text = f"タイトル: {patent.get('title', '')}\n"
        full_text += f"概要: {patent.get('abstract', '')}\n"
        full_text += f"請求項: {patent.get('claims', '')}"
        
        # テキストを分割
        texts = text_splitter.split_text(full_text)
        
        # 分割したテキストをDocumentオブジェクトに変換
        documents = [Document(page_content=text, metadata=patent) for text in texts]
        
        # WeaviateにDocumentを追加
        vectorstore.add_documents(documents)
    
    print(f"{len(patents)}件の特許データをインポートしました")

# 特許検索ツール
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
patent_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

patent_search_tool = Tool(
    name="PatentSearch",
    func=patent_qa.run,
    description="特許情報を検索するツール。技術トピック、発明者、特許番号などで検索できます。"
)

# 特許分析ツール
def analyze_patent_trends(query):
    """特許のトレンドを分析する"""
    docs = retriever.get_relevant_documents(query)
    
    # 分析用のプロンプト
    analysis_prompt = f"""
    以下の特許情報に基づいて、{query}に関する技術トレンドを分析してください。
    重要なパターン、革新的な技術、主要な企業や発明者を特定し、
    この分野の発展の方向性について洞察を提供してください。
    
    特許情報:
    {docs}
    """
    
    return llm.predict(analysis_prompt)

patent_analysis_tool = Tool(
    name="PatentAnalysis",
    func=analyze_patent_trends,
    description="特定の技術分野や企業に関する特許のトレンドを分析するツール。"
)

# 類似特許検索ツール
def find_similar_patents(patent_description):
    """類似特許を検索する"""
    docs = retriever.get_relevant_documents(patent_description)
    
    # 結果整形用のプロンプト
    format_prompt = f"""
    以下の特許情報から、入力された発明アイデア「{patent_description}」に類似する特許を
    特定し、簡潔にまとめてください。各特許について、タイトル、概要、特許番号、
    および元のアイデアとの類似点を説明してください。
    
    特許情報:
    {docs}
    """
    
    return llm.predict(format_prompt)

similar_patent_tool = Tool(
    name="SimilarPatentFinder",
    func=find_similar_patents,
    description="入力された発明アイデアや技術説明に類似する既存特許を検索するツール。"
)

# 特許出願アドバイスツール
def patent_filing_advice(invention_description):
    """特許出願のアドバイスを提供する"""
    docs = retriever.get_relevant_documents(invention_description)
    
    advice_prompt = f"""
    以下の発明アイデア「{invention_description}」と関連する既存特許情報に基づいて、
    特許出願に関するアドバイスを提供してください。差別化のポイント、強調すべき革新的側面、
    出願戦略について具体的な提案を行ってください。
    
    関連特許情報:
    {docs}
    """
    
    return llm.predict(advice_prompt)

patent_advice_tool = Tool(
    name="PatentAdvice",
    func=patent_filing_advice,
    description="特許出願戦略についてアドバイスを提供するツール。既存特許との差別化方法を提案します。"
)

# ツールを組み合わせたエージェントの作成
tools = [
    patent_search_tool,
    patent_analysis_tool,
    similar_patent_tool,
    patent_advice_tool
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# メイン関数
def main():
    print("特許調査エージェントを起動しました。")
    print("データをインポートするには 'import [ファイルパス]' と入力してください。")
    print("終了するには 'exit' と入力してください。")
    print("それ以外の入力は特許調査クエリとして処理されます。")
    
    while True:
        user_input = input("\n> ")
        
        if user_input.lower() == 'exit':
            print("エージェントを終了します。")
            break
        
        elif user_input.lower().startswith('import '):
            file_path = user_input[7:].strip()
            print(f"{file_path} からデータをインポートします...")
            patents = load_patent_data(file_path)
            if patents:
                import_patents_to_weaviate(patents)
            else:
                print("インポートするデータがありませんでした。")
        
        else:
            try:
                result = agent.run(user_input)
                print("\n回答:")
                print(result)
            except Exception as e:
                print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()