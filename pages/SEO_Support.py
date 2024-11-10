import streamlit as st
import google.generativeai as genai

# Streamlitのアプリタイトル
st.title("ブログ記事SEO自動生成アプリ")

# APIキーの設定
genai.configure(api_key=st.secrets["gemini_key"])

# ユーザーの入力を受け取る
title = st.text_input("ブログ記事のタイトルを入力してください")
topic = st.text_area("トピックをいくつか入力してください (カンマで区切ってください)")

# フッターを作成
st.markdown("""
<footer>
  <p>Creator : k.kansuke823@gmail.com</p>
</footer>
""", unsafe_allow_html=True)



if st.button("記事生成"):
    if not title or not topic:
        st.warning("タイトルとトピックを入力してください")
    else:
        # プロンプトの作成
        prompt = f"""あなたは、SEOを意識したブログ記事を執筆するAIです。以下の「テーマ」と「トピック」に基づいて、ブログ記事の効果的なアウトラインを考え、記事を作成してください。
                     ### テーマ: {title}
                     ### トピック: {topic}

                     - 読者対象: 専門的な技術を知らない人でもわかりやすいように解説してください。
                     - 記事の目的: 読者にその技術やトピックについて理解させ、簡単に試せるようにする。
                     - SEOを意識して、関連するキーワードを適切に盛り込みつつ、自然な形で記事を構成してください。
                     - アウトライン:
                     1. **イントロダクション**: トピックの概要とその重要性を説明。
                     2. **基本概念の説明**: まずは初心者向けに基本的な用語や概念を説明。
                     3. **実際の使い方**: ユーザーが手を動かして試せるよう、具体的なステップを示す。
                     4. **実際の事例**: トピックに関連するユースケースや実際の成功事例を紹介。
                     5. **結論**: まとめとして、学んだことを振り返り、さらなる参考リソースや次に試すべきことを示す。

                     - 本文の長さは2000～3000文字程度で、必要に応じてセクションを分けてください。
                     - わかりやすく、かつ簡潔に説明し、読者が理解しやすい表現を心がけてください。
                     - 複雑な技術用語は、簡単な言葉で説明したり、具体的な例を用いて解説してください。

                     生成した記事のアウトラインに沿って、記事本文を作成してください。
                     作成した記事本文のみ回答してください。"""

        # モデルを指定してコンテンツを生成
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt, stream=True)

        # 生成されたコンテンツをリアルタイムで更新
        output_area = st.empty()  # 空の領域を作成して、ここに徐々にテキストを表示する

        generated_text = ""
        for chunk in response:  # レスポンスを順次受け取る
            generated_text += chunk.text  # 受け取ったテキストを追加
            output_area.write(generated_text)  # 現在の内容を表示


