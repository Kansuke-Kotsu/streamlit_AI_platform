import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import time


# Show title and description.
st.title("💬 Simple Chatbot")
st.write("This is a simple chatbot that uses several models to generate responses. ")

# フッターを作成
st.markdown("""
<footer>
  <p>Creator : k.kansuke823@gmail.com</p>
</footer>
""", unsafe_allow_html=True)

# API Keyをセット
os.environ["GOOGLE_API_KEY"] = st.secrets["gemini_key"]

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"
    )

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

        # Stream the response character by character
        text = ""
        for char in ai_msg.content:
            text = text + char
            response_placeholder.markdown(text, unsafe_allow_html=True)
            time.sleep(0.01)  # 文字間の遅延を設定

        # Store the complete response in session state
        st.session_state.messages.append(["assistant", ai_msg.content])