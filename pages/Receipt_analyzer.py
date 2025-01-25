import streamlit as st
from PIL import Image
import openai
import os
import json
import base64
import io

# OpenAI APIキーの設定
openai.api_key = st.secrets["OPENAI_API_KEY"]

# PIL.Imageオブジェクトをバイト列に変換する 
def image_to_bytes(image, format='PNG'):
    with io.BytesIO() as buffered:
        image.save(buffered, format=format)
        return buffered.getvalue()

# 画像をBase64形式に変換する 
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def send_image_to_openai(image_base64):
    messages = [
        {
            "role": "user",
            "content": (
                "以下のレシート画像を解析し、以下の情報を含むJSON形式で返してください。\n\n"
                "必要な情報:\n"
                "1. 金額\n"
                "2. 勘定科目\n"
                "3. 概要\n\n"
                "レスポンスのテンプレート:\n"
                "{\n"
                '  "日付": "例: 08/23",\n'
                '  "金額": "例: 1,000円",\n'
                '  "勘定科目": "例: 接待交際費",\n'
                '  "概要": "例: 食事"\n'
                "}"
            )
        },
        {
            "role": "user",
            "content": f"data:image/png;base64,{image_base64}"
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # 例: gpt-4
        messages=messages
    )
    return response

def main():
    # カメラ入力ウィジェット
    uploaded_image = st.camera_input("カメラで写真を撮影してください")
    if uploaded_image is not None:
        # アップロードされた画像を表示
        image = Image.open(uploaded_image)
        st.image(image, caption='アップロードされた写真', use_column_width=True)

        # 解析開始ボタン
        if st.button("画像を解析する"):
            with st.spinner("画像を解析中..."):
                # 画像をバイト列に変換
                image_bytes = image_to_bytes(image, format='PNG')

                # 画像をBase64形式にエンコード
                image_base64 = encode_image(image_bytes)

                # OpenAIに画像を送信して解析
                response = send_image_to_openai(image_base64)
                assistant_message = response['choices'][0]['message']['content']
                
                print(assistant_message)
                st.write(assistant_message)

if __name__ == "__main__":
    main()