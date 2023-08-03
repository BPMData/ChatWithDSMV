import streamlit as st
import ast  # for converting embeddings saved as strings back to arrays
import pandas as pd  # for storing text and embeddings data
import os
from main import ask_stream, OPENAI_API_KEY
from streamlit_extras.colored_header import colored_header
from google.cloud import storage
st.set_page_config(page_title="DSM-5 Chat", page_icon='Ψ', layout='wide')



from google.cloud import storage

@st.cache_resource
def read(bucket_name, blob_name):
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html

    with blob.open("r", encoding='utf-8') as f:
        df = pd.read_csv(f)
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    return df


df = read('chatwithdsm5.appspot.com', 'dsmv_400.csv')


st.title("🤖⇢📚Ψ⇢💬 Talk to ChatGPT after it has 'read' the DSM-5.")
st.subheader("Powered by ChatGPT-3.5-Turbo. Best viewed on PC or tablet.")
colored_header(label='Ask a question below, and ChatGPT will answer it using its knowledge of the DSM-5!', description="", color_name="orange-70")

# Declare our constants:
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


# @st.cache_resource
# def load_data(file_path):
#     df = pd.read_csv(file_path)
#     df['embedding'] = df['embedding'].apply(ast.literal_eval)
#     return df




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