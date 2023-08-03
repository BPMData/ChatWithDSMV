import streamlit as st
st.set_page_config(page_title="DSM-5 Chat", page_icon='Ψ', layout='wide')
import ast  # for converting embeddings saved as strings back to arrays
import pandas as pd  # for storing text and embeddings data
from main import ask_stream
from streamlit_extras.colored_header import colored_header

st.title("🤖⇢📚Ψ⇢💬 Talk to ChatGPT after it has 'read' the DSM-5.")
colored_header(label="Powered by ChatGPT-3.5-Turbo. Best viewed on PC or tablet.", description="", color_name="orange-70")

# Declare our constants:
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
# Ok

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Please enter your query for the DSM-5:"):
    # Save the message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

# Provide chatbot response
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ''
        for response in ask_stream(
                prompt,
                model='gpt-3.5-turbo',
                stream=True
        ):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


# if __name__ == "__main__":
print("Streamlit app run from main.")