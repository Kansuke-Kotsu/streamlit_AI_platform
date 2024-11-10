import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# セキュリティ上の注意：
# APIキーをコード内に直接記載するのは避け、環境変数やStreamlitのシークレットマネージャーを使用してください。
# 例: os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# LLMを初期化
os.environ["GOOGLE_API_KEY"] = st.secrets["gemini_key"]
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7
    )

llm_short = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=150
    )

# セッションステートの初期化
if 'stage' not in st.session_state:
    st.session_state.stage = None

# 各フロー用のセッションステートを初期化
for key in ['step', 'requirements', 'recommendation', 'period', 'budget', 'detailed_advice', 'next_questions', 'chat_history']:
    if key not in st.session_state:
        st.session_state[key] = None

def send_email(subject, body):
    smtp_server = st.secrets["smtp_server"]
    smtp_port = st.secrets["smtp_port"]
    sender_email = st.secrets["sender_email"]
    sender_password = st.secrets["sender_password"]
    recipient_email = st.secrets["recipient_email"]

    # メールのセットアップ
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # SMTPサーバーに接続してメールを送信
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # TLSを開始
        server.login(sender_email, sender_password)
        server.send_message(msg)

# 関数定義
def get_tech_recommendation(requirements):
    prompt = (
        "以下のプロジェクト概要に基づいて、以下の項目ごとに推奨事項とその理由を提供してください。\n"
        "各項目はJSON形式で出力し、推奨事項とその理由を含むようにしてください。\n"
        "出力フォーマットの例:\n"
        "{\n"
        '  "推奨するプログラミング言語": [\n'
        '    {"言語": "Python", "理由": "Pythonは学習が容易であり、豊富なライブラリが利用可能です。"},\n'
        '    {"言語": "JavaScript", "理由": "Web開発において広く使用されており、多くのフレームワークがあります。"}\n'
        '  ],\n'
        '  "ツール、開発環境": [\n'
        '    {"ツール": "Visual Studio Code", "理由": "拡張機能が豊富で、高いカスタマイズ性を持ちます。"},\n'
        '    {"ツール": "Git", "理由": "バージョン管理システムとして標準的に使用されています。"}\n'
        '  ],\n'
        '  "必要なコストと期間": {\n'
        '    "コスト": "100万円～数億円（開発規模、機能、採用するAI技術によって大きく変動）",\n'
        '    "期間": "6ヶ月～数年（開発規模、機能、採用するAI技術によって大きく変動）"\n'
        '  },\n'
        '  "その他検討が必要なこと": [\n'
        '    "セキュリティ対策",\n'
        '    "スケーラビリティ"\n'
        '  ]\n'
        "}\n\n"
        f"プロジェクト概要: {requirements}\n"
    )
    response = llm.invoke(prompt)
    try:
        # JSON部分を抽出
        response_content = response.content
        start = response_content.find("{")
        end = response_content.rfind("}") + 1
        json_str = response_content[start:end]
        recommendations = json.loads(json_str)

        # メールの送信
        subject = "新しいプロジェクト概要が提出されました"
        body = f"立案段階:\n\n{requirements}"
        send_email(subject, body)

        return recommendations
    except json.JSONDecodeError:
        # エラーハンドリング: JSON解析に失敗した場合
        return {
            "推奨するプログラミング言語": "情報が取得できませんでした。",
            "ツール、開発環境": "情報が取得できませんでした。",
            "必要なコストと期間": "情報が取得できませんでした。",
            "その他検討が必要なこと": "情報が取得できませんでした。"
        }

def get_detailed_advice(requirements, period, budget):
    prompt = (
        f"プロジェクトの要件: {requirements}\n"
        f"期間: {period}\n"
        f"予算: {budget}円\n"
        f"これらの情報に基づいて、リソース配分やスケジュール管理の提案をしてください。"
    )
    response = llm.invoke(prompt)

    # メールの送信
    subject = "新しいプロジェクト概要が提出されました"
    body = f"実行段階:\n\n{prompt}"
    send_email(subject, body)

    return response.content

def get_next_questions(context_data):
    prompt = (
        "以下のコンテキストに基づいて、ユーザーが次に尋ねる可能性が高い質問を3つ提案してください。\n"
        "出力はJSON形式で、各質問をリストとして含めてください。\n"
        "出力フォーマットの例:\n"
        "{\n"
        '  "next_questions": [\n'
        '    "質問1",\n'
        '    "質問2",\n'
        '    "質問3"\n'
        '  ]\n'
        "}\n\n"
        f"コンテキスト: {context_data}\n"
    )
    response = llm_short.invoke(prompt)
    try:
        # JSON部分を抽出
        response_content = response.content
        start = response_content.find("{")
        end = response_content.rfind("}") + 1
        json_str = response_content[start:end]
        questions_json = json.loads(json_str)
        questions = questions_json.get("next_questions", [])
        
        return questions
    except json.JSONDecodeError:
        # エラーハンドリング: JSON解析に失敗した場合
        return ["情報が取得できませんでした。"]

def reset_session():
    for key in ['stage', 'step', 'requirements', 'recommendation', 'period', 'budget', 'detailed_advice', 'next_questions', 'chat_history']:
        st.session_state[key] = None

# UI構築
st.title("PM支援AIツール")

# ステージの選択
if st.session_state.stage is None:
    st.header("あなたのプロジェクトの状況を教えてください")
    stage = st.radio(
        "プロジェクトの現在の段階を選択してください：",
        ("立案段階：どのように開発を始めたらいいか（手法・予算など）を相談したい",
         "実行段階：ある程度計画は決まっているので、より具体的な相談がしたい",
         "進行中：すでに実行中で、今の状況を踏まえて今後について相談したい")
    )
    if st.button("選択"):
        if "立案段階" in stage:
            st.session_state.stage = "plan"
        elif "実行段階" in stage:
            st.session_state.stage = "execute"
        elif "進行中" in stage:
            st.session_state.stage = "in_progress"
        st.rerun()
else:
    if st.session_state.stage == "plan":
        # 立案段階のフロー
        st.header("プロジェクトの概要を入力してください")
        if st.session_state.step is None or st.session_state.step == 1:
            with st.form(key='plan_form'):
                project_overview = st.text_area("プロジェクト概要", height=150)
                submit = st.form_submit_button("送信")
            if submit and project_overview:
                st.session_state.requirements = project_overview
                st.session_state.recommendation = get_tech_recommendation(project_overview)
                st.session_state.step = 2
                st.rerun()
        elif st.session_state.step == 2:
            st.header("おすすめの技術スタックとその他の情報")
            recommendations = st.session_state.recommendation

            # 推奨するプログラミング言語の表示の改善
            st.subheader("推奨するプログラミング言語")
            languages = recommendations.get("推奨するプログラミング言語", "情報がありません。")
            if isinstance(languages, list):
                for lang in languages:
                    language = lang.get('言語', '不明')
                    reason = lang.get('理由', '理由がありません。')
                    st.markdown(f"- {language}: {reason}")
            else:
                st.info(languages)

            # ツール、開発環境の表示
            st.subheader("ツール、開発環境")
            tools = recommendations.get("ツール、開発環境", "情報がありません。")
            if isinstance(tools, list):
                for tool in tools:
                    tool_name = tool.get('ツール', '不明')
                    tool_reason = tool.get('理由', '理由がありません。')
                    st.markdown(f"- {tool_name}: {tool_reason}")
            else:
                st.info(tools)

            # 必要なコストと期間の表示
            st.subheader("必要なコストと期間")
            cost_time = recommendations.get("必要なコストと期間", "情報がありません。")
            if isinstance(cost_time, dict):
                cost = cost_time.get("コスト", "不明")
                period = cost_time.get("期間", "不明")
                st.markdown(f"- コスト: {cost}")
                st.markdown(f"- 期間: {period}")
            else:
                st.info(cost_time)

            # その他検討が必要なことの表示
            st.subheader("その他検討が必要なこと")
            others = recommendations.get("その他検討が必要なこと", "情報がありません。")
            if isinstance(others, list):
                for item in others:
                    st.markdown(f"- {item}")
            else:
                st.info(others)
            
            if st.button("トップページに戻る"):
                reset_session()
                st.rerun()

    elif st.session_state.stage == "execute":
        # 実行段階のフロー（既存のWebアプリ）
        if st.session_state.step is None:
            st.session_state.step = 1

        if st.session_state.step == 1:
            st.header("ソフトウェアの要件を入力してください")
            with st.form(key='requirements_form'):
                requirements = st.text_area("要件", height=150)
                submit = st.form_submit_button("送信")
            if submit and requirements:
                st.session_state.requirements = requirements
                st.session_state.recommendation = get_tech_recommendation(requirements)
                st.session_state.step = 2
                st.rerun()

        elif st.session_state.step == 2:
            st.header("プロジェクトの期間と予算を入力してください")
            with st.form(key='details_form'):
                period = st.text_input("期間（例: 6ヶ月）")
                budget = st.number_input("予算（円）", min_value=0, step=10000)
                submit = st.form_submit_button("送信")
            if submit and period and budget:
                st.session_state.period = period
                st.session_state.budget = budget
                st.session_state.detailed_advice = get_detailed_advice(
                    st.session_state.requirements,
                    period,
                    budget
                )
                context_data = {
                    'requirements': st.session_state.requirements,
                    'period': period,
                    'budget': budget
                }
                st.session_state.next_questions = get_next_questions(context_data)
                st.session_state.step = 3
                st.rerun()

        elif st.session_state.step == 3:
            # 詳細アドバイスの表示
            st.header("詳細アドバイス")
            st.success(st.session_state.detailed_advice)

            # 次に知りたいことの表示
            st.header("次に知りたいことは？")
            next_questions = st.session_state.next_questions
            if isinstance(next_questions, list):
                for idx, question in enumerate(next_questions, 1):
                    if st.button(f"{idx}. {question}"):
                        st.write(f"**{question}**")
                        # ここに追加の対話ロジックを実装可能
            else:
                st.info("次の質問を取得できませんでした。")

            if st.button("トップページに戻る"):
                reset_session()
                st.rerun()

    elif st.session_state.stage == "in_progress":
        # 進行中のフロー（シンプルなChatBot）
        st.header("チャットボットと対話してください")
        if "messages" not in st.session_state:
            st.session_state.messages = []

            # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message[0]):
                st.markdown(message[1])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := st.chat_input("What is up?"):

            # Store and display the current prompt.
            st.session_state.messages.append(["user", prompt])
            with st.chat_message("user"):
                st.markdown(prompt)

            # Create a chat message for the assistant
            with st.chat_message("assistant"):
                # Create a placeholder for the response
                response_placeholder = st.empty()

                # Call the LLM and stream the response
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
                ai_msg = llm.invoke(st.session_state.messages)
                # メールの送信
                subject = "新しいプロジェクト概要が提出されました"
                body = f"進行中:\n\n{prompt}"
                send_email(subject, body)

                # Stream the response character by character
                text = ""
                for char in ai_msg.content:
                    text = text + char
                    response_placeholder.markdown(text, unsafe_allow_html=True)
                    time.sleep(0.01)  # 文字間の遅延を設定

                # Store the complete response in session state
                st.session_state.messages.append(["assistant", ai_msg.content])
        

        if st.button("トップページに戻る"):
            reset_session()
            st.rerun()


# CSSファイルを作成
with open("../style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# フッターを作成
st.markdown("""
<footer>
  <p>Creator : k.kansuke823@gmail.com</p>
</footer>
""", unsafe_allow_html=True)