import streamlit as st
import requests
import io
from PIL import Image

API_TOKEN = st.secrets["huggingface"]

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# ユーザーからの入力を受け取る
prompt = st.text_input("画像にしたいテキストを入力してください:", "")

# 画像の生成ボタン
if st.button("画像を生成"):
    if prompt.strip() == "":
        st.warning("テキストを入力してください。")
    else:
        with st.spinner("画像を生成中...(1分くらいかかります)"):
            try:
                response = requests.post(API_URL, headers=headers, json=f"input: {prompt}")
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes))
                
                # 画像を表示
                st.image(image)
                
            except Exception as e:
                st.error(f"画像生成中にエラーが発生しました: {e}")