import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

# you can add more configuration parameters here
CONFIG = {'configurable' : {'thread_id' : "thread_1"}} 
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
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata  in chatbot.stream(
                #initial state 
                {"messages": [HumanMessage(content="Hello, how are you?")]},
                #config 
                config = {'configurable' : {'thread_id' : "thread_1"}},
                #mode
                stream_mode = 'messages')
            )
        
        st.session_state['message_history'].append({"role": "assistant", "content": ai_message})

