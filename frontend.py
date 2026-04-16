import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# ______________________________________________________________________
#                             Utility Functions
# ______________________________________________________________________

def generate_id():
    """
    Description:

    .
    """
    thread = uuid.uuid4()
    return thread

def reset_chat():
    """
    Description:

    .
    """
    thread_id = generate_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    """
    Description:

    Parameters
    ----------
    :param thread_id: INSERT DESCRIPTION
    :type thread_id: type

    .
    """
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    """
    Description:

    Parameters
    ----------
    :param thread_id: INSERT DESCRIPTION
    :type thread_id: type

    .
    """
    return chatbot.get_state(config={"configurable": {"thread_id": thread_id}}).values['messages']

def generate_title(user_message):
    """
    Description:

    Parameters
    ----------
    :param user_message: INSERT DESCRIPTION
    :type user_message: type

    .
    """
    prompt = f"""
    Generate a short conversation title in 2-3 words only.
    Message: {user_message}
    Title:
    """
    # Use a dummy thread_id so this prompt doesn't save into the main chat history
    dummy_config = {"configurable": {"thread_id": "title_gen_" + str(uuid.uuid4())}}
    
    response = chatbot.invoke({"messages": [HumanMessage(content=prompt)]}, config=dummy_config)
    
    # Bug fixed: Removed .values to access dictionary directly
    return response['messages'][-1].content.strip('" \n') 

# ______________________________________________________________________
#                             Setup
# ______________________________________________________________________

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_id()

if "chat_thread" not in st.session_state:
    st.session_state['chat_thread'] = []

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}
    
add_thread(st.session_state['thread_id'])

# ______________________________________________________________________
#                             SideBar
# ______________________________________________________________________

st.sidebar.title("Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations : ")

for thread_id in st.session_state['chat_thread'][::-1]:
    chat_title = st.session_state["chat_titles"].get(thread_id, "New Chat")
    
    # key=str(thread_id) is mandatory to prevent duplicate keys error
    if st.sidebar.button(chat_title, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp = []
        for sms in messages:
            if isinstance(sms, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp.append({"role": role, "content": sms.content})
        
        st.session_state['message_history'] = temp
        st.rerun()

# Load history on screen
for meg in st.session_state['message_history']:
    with st.chat_message(meg["role"]):
        st.text(meg["content"])

userinput = st.chat_input("Type your message here...")

# ____________________________________________________________________
#                                 Main
# ____________________________________________________________________

if userinput:
    current_thread = st.session_state['thread_id']
    
    # 1. Generate Title if it's the first message of the thread
    if current_thread not in st.session_state["chat_titles"]:
        title = generate_title(userinput)
        st.session_state["chat_titles"][current_thread] = title

    # 2. Add message to history & display
    st.session_state['message_history'].append({"role": "user", "content": userinput})
    with st.chat_message("user"):
        st.text(userinput)

    CONFIG = {
        'configurable' : {
            'thread_id' : current_thread
        }
    }
    
    # 3. Chatbot Integration
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=userinput)]},
                config = CONFIG,
                stream_mode = 'messages'
            )
        )
        
        st.session_state['message_history'].append({"role": "assistant", "content": ai_message})