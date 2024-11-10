import streamlit as st

# Streamlitのアプリタイトル
st.title("PowerPoint自動生成")
st.write("開発中")

# CSSファイルを作成
with open("../style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# フッターを作成
st.markdown("""
<footer>
  <p>Creator : k.kansuke823@gmail.com</p>
</footer>
""", unsafe_allow_html=True)