import streamlit as st

st.title("Ai am")
st.write("生成AIを用いた様々なサービスを提供するプラットフォームです。\n")
st.write("←から機能を選んで試してみてください。\n")


# CSSファイルを作成
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# カラムの配置
# 1行目の3つのカラム
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '''
        <a href="/Blog_Generator">
            <div class="container">
                <h3>Blog Sentence Generator</h3>
                <p>AIを用いて効果的なブログ文章を自動生成します。コンテンツ作成の時間を短縮できます。</p>
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '''
        <a href="/ChatBot">
            <div class="container">
                <h3>Simple ChatBot</h3>
                <p>シンプルなチャットボットを提供。ユーザーとの対話を自動化し、サポート業務を効率化します。</p>
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        '''
        <a href="/Image_Generator">
            <div class="container">
                <h3>Image Generator</h3>
                <p>AIを活用して高品質な画像を自動生成。デザインやコンテンツ作成に役立ちます。</p>
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

# 2行目の3つのカラム
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
        '''
        <a href="/Project_Manegement">
            <div class="container">
                <h3>PM Support Tool</h3>
                <p>プロジェクト管理を支援するツール。タスクの進捗管理やチームのコミュニケーションを効率化します。</p>
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        '''
        <a href="/WebApp_Generator">
            <div class="container">
                <h3>Web Application Generator</h3>
                <p>簡単にウェブアプリケーションを生成。迅速なプロトタイピングや開発に最適です。</p>
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

with col6:
    st.markdown(
        '''
        <div class="container">
            <h3>その他の機能</h3>
            <p>多様なAIサービスを開発中！詳細はお問い合わせください。</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

# フッターを作成
st.markdown("""
            <footer>
                <p>Creator : k.kansuke823@gmail.com</p>
            </footer>
""", unsafe_allow_html=True)