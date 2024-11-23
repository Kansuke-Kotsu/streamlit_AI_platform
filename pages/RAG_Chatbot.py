import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import os
import tempfile

# Streamlitのページ設定
st.set_page_config(page_title="📄 Google Search RAG Chatbot")

# タイトルと説明
st.title("📄 Retrieval-Augmented Generation (RAG) Chatbot with Google Search")
st.write("""
ユーザーの質問に基づいてGoogle検索を行い、最新の情報を取得して回答を提供します。
このアプリを使用するには、OpenAIとSerpAPIのAPIキーが必要です。
以下のリンクからAPIキーを取得してください。
(OpenAI: https://platform.openai.com/account/api-keys, 
SerpAPI: https://serpapi.com/)
""")

# APIキーの取得と確認
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ""
if 'serpapi_api_key' not in st.session_state:
    st.session_state['serpapi_api_key'] = ""

# 入力フォーム
with st.form("apikey_form"):
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state['openai_api_key'])
    serpapi_api_key = st.text_input("Enter your SerpAPI Key", type="password", value=st.session_state['serpapi_api_key'])
    submitted = st.form_submit_button("Save API Keys")

    if submitted:
        st.session_state['openai_api_key'] = openai_api_key
        st.session_state['serpapi_api_key'] = serpapi_api_key
        st.success("APIキーが保存されました。")

# 確認
if not st.session_state['openai_api_key'] or not st.session_state['serpapi_api_key']:
    st.warning("OpenAI APIキーとSerpAPIキーを入力してください。")
    st.stop()

openai_api_key = st.session_state['openai_api_key']
serpapi_api_key = st.session_state['serpapi_api_key']

# パラメータ設定
with st.sidebar:
    st.subheader("パラメータ設定")
    chunk_size = st.number_input("Chunk Size", min_value=100, max_value=5000, value=1000, step=100)
    chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=1000, value=200, step=50)
    num_results = st.number_input("Number of Google Search Results", min_value=1, max_value=10, value=5, step=1)


# 質問の入力
question = st.text_area(
    "質問を入力してください:",
    placeholder="例: 最新のAI技術について教えてください。",
)

if st.button("回答を生成"):
    if not question:
        st.warning("質問を入力してください。")
    else:
        with st.spinner("Google検索で情報を取得中..."):
            # SerpAPIを使用してGoogle検索を行う
            search = GoogleSearch({
                "q": question,
                "api_key": serpapi_api_key,
                "num": num_results,  # 上位num_results件の結果を取得
            })
            results = search.get_dict()

            if "organic_results" not in results:
                st.error("検索結果が見つかりませんでした。")
                st.stop()

            organic_results = results["organic_results"]

            # 各検索結果からテキストを取得
            extracted_texts = []
            for result in organic_results:
                try:
                    link = result.get("link")
                    if link:
                        response = requests.get(link, timeout=10)
                        soup = BeautifulSoup(response.text, "html.parser")
                        # ページのテキストを取得
                        texts = soup.stripped_strings
                        page_text = " ".join(texts)
                        extracted_texts.append(page_text)
                except Exception as e:
                    st.warning(f"リンク {link} の処理中にエラーが発生しました: {e}")

            if not extracted_texts:
                st.error("有効な検索結果からテキストを取得できませんでした。")
                st.stop()

            # テキストをチャンク分け
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = []
            for text in extracted_texts:
                chunks.extend(text_splitter.split_text(text))

        with st.spinner("ベクトルストアを構築中..."):
            # Embeddingsの作成
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            # 一時ディレクトリにChromaデータベースを作成
            with tempfile.TemporaryDirectory() as tempdir:
                vectorstore = Chroma.from_texts(
                    texts=chunks,
                    embedding=embeddings,
                    persist_directory=os.path.join(tempdir, "chroma")
                )
                # 類似度検索を実行
                docs = vectorstore.similarity_search(question, k=4)
                
        with st.spinner("ChatGPTが回答を生成中..."):
            # Chatモデルの初期化
            llm = ChatOpenAI(
                openai_api_key=openai_api_key,
                model_name="gpt-4o-mini",
                temperature=0.5  # 回答の創造性の調整
            )

            # コンテキストの準備
            context = "\n\n".join([doc.page_content for doc in docs])

            # メッセージの構築
            messages = [
                SystemMessage(content="You are a helpful assistant that provides information based on the provided context."),
                HumanMessage(content=f"Context: {context}\n\nQuestion: {question}")
            ]

            # レスポンスの生成
            response = llm(messages)

        # レスポンスの表示
        st.success("**回答:**")
        st.write(response.content)