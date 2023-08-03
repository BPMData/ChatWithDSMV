import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header

st.set_page_config(page_title="Notes and Warnings", page_icon='❔⚠', layout='wide')
st.title('❔⚠️ Disclaimers and Things to Note')
colored_header(label='All the rights related to the DSM-5 belong to the American Psychological Association.', description="", color_name="orange-70")

c = st.container()
c.write('I did this for fun, as a proof of concept, and because I thought you might find it interesting. Not only do I not make money of off this app, it actually costs me money every time you use it.')
c.write('')
c.write("This app is not intended to be your therapist or provide a diagnosis. Diagnoses can only be given by licensed professionals, not chatbots. This app is primarily a proof of concept, intended at most to be a reference for professionals already knowledgeable in the field. If you don't know the definitions of the words 'lability,' 'operationalization' and 'comorbidity' already, this app probably isn't for you. If you want a therapist, try Google Bard, Microsoft Bing Chat in Creative mode, BonziBuddy, or better yet, an actual human being.")

st.divider()
st.warning("The purpose of this chatbot is to answer questions about psychology with greater technical fidelity by making use of the DSM-5. To this end, and to avoid the rabbit holes AI sometimes falls down into over the course of longer, iterative conversations, all of the available 'memory' of the chatbot was dedicated to referencing the DSM-5. As a result, this chatbot intentionally CANNOT remember your prior questions or its own prior responses. If you want to tweak your output, try asking your question in a different way. Prompts such as, 'Restate your previous answer as if you had a target audience of 7th graders,' or 'Can you give me that information in a table?' will NOT work.", icon="⚠️")
st.divider()

take_me_home = st.button("Take me home!")
if take_me_home:
    switch_page("Chat_With_DSM-5")