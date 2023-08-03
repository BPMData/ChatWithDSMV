import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header

st.set_page_config(page_title="🧮 How It Works.py", page_icon='🧮📊', layout='wide')
st.title('🧮📊 The Math Behind the Model')
colored_header(label='How does this work? Did ChatGPT really read over 900 pages of reference material?', description="", color_name="orange-70")

c = st.container()
c.write("No, ChatGPT can't 'remember' more than a few thousand words at once. What this web app does is break down a large text into hundreds of smaller pieces, and assign each piece of the text a number string known as an 'embedding.'  An embedding is a long sequence of numbers that collectively represent the contents of that particular piece of the text. Pieces with similar content will have many similar numbers in their number strings.")
c.write("When you ask the app a question, it asks ChatGPT to convert your question into a number string, then scans the list of number strings in its memory to find those that are the most similar to the number string of your question. The app then takes the words associated with those most-similar number strings and gives them to ChatGPT to use as reference material. You're not seeing it, but if you ask a question such as, 'How would I know if I'm depressed?', the question ChatGPT is actually answering is, 'Look at these five or six pages of reference material, and tell me, how would I know if I'm depressed?'")
c.write("If the app cannot find any number strings in its memory that are similar to the number string of your question, it should (hopefully!) simply refuse to answer it, as your question is probably off-topic and that's what I told it to do when asked irrelevant questions. If it does answer, know that you're just getting a generic canned response from the basic ChatGPT-3.5-Turbo, and in fact almost certainly a worse answer than if you asked regular ChatGPT via OpenAI's web site.")
c.write("In theory, this web app would work with any text, from a book, to a series of books, to an anthology of poetry, to hundreds of thousands of pages of documents uncovered in the discovery phase of a trial. This particular app, however, improves the quality of its output by using vocabulary specific to the mental health field inside its code, so it would probably give you some pretty weird answers if you loaded 'The Lord of the Rings' into it.")

st.divider()
take_me_home = st.button("Take me home!")
if take_me_home:
    switch_page("Chat With DSM-5")
