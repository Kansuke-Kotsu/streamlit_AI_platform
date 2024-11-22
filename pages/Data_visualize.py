import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import pandas as pd
import io
import os
import matplotlib.pyplot as plt

openai_api_key = st.secrets["OPENAI_API_KEY"] # Streamlit secretsを使用する場合
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

st.title("Data Visualization App")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            df = None

        if df is not None:
            # プロンプトの作成
            prompt_template = """
            Generate Python code using matplotlib to visualize the data in the following Pandas DataFrame.  The DataFrame is:
            {data}
            Generate code that creates a suitable plot.  Consider different plot types (e.g., line chart, bar chart, scatter plot) based on the data.  Return only the code, do not include any explanations.
            """
            prompt = PromptTemplate(template=prompt_template, input_variables=["data"])

            # LLMを使ってコードを生成
            code = llm(prompt.format(data=df.head().to_string()))

            # **セキュリティ上の懸念から、exec()の使用は推奨されません。**
            # 以下は危険な例です。本番環境では使用しないでください。
            try:
                # 危険な exec() の使用
                exec(code, globals(), locals())
                st.pyplot(plt)  # Matplotlibの図を表示
            except Exception as e:
                st.error(f"Error generating or executing code: {e}")

    except Exception as e:
        st.error(f"Error reading file: {e}")