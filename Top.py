import streamlit as st

st.title("Ai am")
st.write("生成AIを用いた様々なサービスを提供するプラットフォームです。\n")
st.write("←から機能を選んで試してみてください。\n")


# CSSファイルを作成
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# フッターを作成
st.markdown("""
            <head>
                <title>Ai am : AI Platform</title>
            </head>
            <footer>
                <p>Creator : k.kansuke823@gmail.com</p>
            </footer>
""", unsafe_allow_html=True)