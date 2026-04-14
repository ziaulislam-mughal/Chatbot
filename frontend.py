import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage


CONFIG = {'configurable' : {'thread_id' : "thread_1"}} # you can add more configuration parameters here
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


#load history
for sms in st.session_state['message_history']:
    with st.chat_message(sms["role"]):
        st.text(sms["content"])

userinput = st.chat_input("Type your message here...")

if userinput:
    st.session_state['message_history'].append({"role": "user", "content": userinput})
    with st.chat_message("user"):
        st.text(userinput)

    #chatbot integrate
    response = chatbot.invoke({
        'messages': [HumanMessage(content=userinput)]},
        config = CONFIG
    )
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)
