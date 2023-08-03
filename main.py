import streamlit as st
import ast  # for converting embeddings saved as strings back to arrays
import openai  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
from scipy import spatial  # for calculating vector similarities for search
import smtplib
import ssl
from google.cloud import storage

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

# Defining secrets manager and setting keys
def access_secret_version(secret_version_id):
    """Return the value of a secret's version"""
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Access the secret version.
    response = client.access_secret_version(name=secret_version_id)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')


OPENAI_API_KEY = access_secret_version("projects/426441628548/secrets/OPENAI_API_KEY_GOOGLE_SECRET/versions/latest")
GMAIL_SEND_KEY = access_secret_version("projects/426441628548/secrets/GMail_SendKey/versions/latest")


# Load the embeddings CSV file, which was pre-generated with a chunk hyperparameter length of 400.
# This part is fairly slow.
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

# Define our search function:
'''Search

Now we'll define a search function that:

Takes a user query and a dataframe with text & embedding columns
Embeds the user query with the OpenAI API
Uses distance between query embedding and text embeddings to rank the texts
Returns two lists:
The top N texts, ranked by relevance
Their corresponding relevance scores
'''


def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 20  # We don't need 100 here, we're never getting to 100 for any one context.
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

# Use the embedding file to generate context:


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'You are a helpful AI assistant. Use this excerpt from The Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition (2013) to answer the question.'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n"""{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget-400  # Set this parameter to whatever makes the chatbot not run out of tokens during its completion.
        ):
            break
        else:
            message += next_article
    return message + question

# Define our asking function
'''
With the search function above, we can now automatically retrieve relevant 
knowledge and insert it into messages to GPT.
Below, we define a function ask that:
Takes a user query 
Searches for text relevant to the query 
Stuffs that text into a message for GPT 
Sends the message to GPT 
Returns GPT’s answer
'''

DSMV_Prompt = ('You are a helpful, professional AI assistant. You are not a '
               'medical or psychological professional, but you use The Diagnostic '
               'and Statistical Manual of Mental Disorders, Fifth Edition to try'
               ' to answer any questions you are asked. The users asking you'
               ' questions ARE medical and psychological professionals, '
               'so answer accordingly. You will answer questions thoroughly, '
               'noting whenever the excerpts you are provided lack sufficient '
               'information to fully answer a question. If your response is '
               'long or complex, you should prioritize returning information '
               'in bullet points or a numbered list.')


def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": DSMV_Prompt},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.6,
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message


def ask_stream(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
    temperature: float = 0.6,
    stream: bool = True
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": DSMV_Prompt},
        {"role": "user", "content": message},
    ]
    for chunk in openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=stream
    ):
        yield chunk['choices'][0].delta.get('content', '')

def send_email(message=""):
    host = "smtp.gmail.com"
    port = 465
    sender_username = "bryan.patrick.a.murphy@gmail.com"
    # password = os.getenv("WebPortfolio_Password")
    password = GMAIL_SEND_KEY

    recipient = "bryan.patrick.a.murphy@gmail.com"

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(sender_username, password)
        server.sendmail(sender_username, recipient, message)

if __name__ == "__main__":
    print(ask('How would I know if my child had attention-deficit hyperactivity disorder?'))
