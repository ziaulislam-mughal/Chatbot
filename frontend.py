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
    dummy_config = {"configurable": {"thread_id": "title_gen_" + str(uuid.uuid4())}}
    response = chatbot.invoke({"messages": [HumanMessage(content=prompt)]}, config=dummy_config)
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

st.sidebar.title("Chat Guru")

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.text("Recent Chats")

for thread_id in st.session_state['chat_thread'][::-1]:
    chat_title = st.session_state["chat_titles"].get(thread_id, "New Chat")
    
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

# ____________________________________________________________________
#                   Load history on screen / Welcome Animation
# ____________________________________________________________________

# Agar chat history khali hai, toh animation show karein
if not st.session_state['message_history']:
    st.markdown(
        """
        <style>
        .welcome-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60vh; /* Screen ke center mein lane ke liye */
        }
        .typewriter {
            font-family: 'Courier New', Courier, monospace;
            color: #ffffff; /* Text color */
            font-size: 2.5em;
            font-weight: bold;
            overflow: hidden; 
            border-right: .15em solid #7b7b7b; /* Cursor color */
            white-space: nowrap; 
            margin: 0 auto;
            letter-spacing: .10em;
            animation: 
                typing 2.5s steps(22, end),
                blink-caret .75s step-end infinite;
        }
        @keyframes typing {
            from { width: 0 }
            to { width: 22ch; } /* Number of characters ke hisaab se width */
        }
        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: #7b7b7b; }
        }
        </style>
        <div class="welcome-container">
            <div class="typewriter">Ready to Chat with Guru </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Agar message history mojood hai toh puray messages show karein
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
    
    # Ek dafa jab AI ka message aa jaye, toh UI update karne ke liye rerun (taki animation remove ho jaye agar issue aaye)
    st.rerun()