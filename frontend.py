import streamlit as st
from backend import chatbot, get_all_threads
from langchain_core.messages import HumanMessage
import uuid


# ============================================================
# Utility Functions
# ============================================================

def generate_id():
    return str(uuid.uuid4())


def reset_chat():

    thread_id = generate_id()

    st.session_state["thread_id"] = thread_id

    add_thread(thread_id)

    st.session_state["message_history"] = []


def add_thread(thread_id):

    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)


def load_conversation(thread_id):

    return chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    ).values["messages"]


def generate_title(user_message):

    prompt = f"""
    Generate a short conversation title in 2-3 words only.
    Message: {user_message}
    Title:
    """

    dummy_config = {
        "configurable": {"thread_id": "title_gen_" + str(uuid.uuid4())}
    }

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=dummy_config
    )

    return response["messages"][-1].content.strip('" \n')


# ============================================================
# Session Setup
# ============================================================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_id()

if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = get_all_threads()

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}

add_thread(st.session_state["thread_id"])


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("Chat Guru")

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.text("Recent Chats")


for thread_id in st.session_state["chat_thread"][::-1]:

    chat_title = st.session_state["chat_titles"].get(thread_id, "New Chat")

    if st.sidebar.button(chat_title, key=str(thread_id)):

        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        temp = []

        for sms in messages:

            role = "user" if isinstance(sms, HumanMessage) else "assistant"

            temp.append({
                "role": role,
                "content": sms.content
            })

        st.session_state["message_history"] = temp

        st.rerun()


# ============================================================
# Welcome Screen
# ============================================================

if not st.session_state["message_history"]:

    st.markdown(
        """
        <style>
        .welcome-container {
            display:flex;
            justify-content:center;
            align-items:center;
            height:60vh;
        }
        .typewriter {
            font-family:monospace;
            font-size:2.5em;
            font-weight:bold;
            overflow:hidden;
            border-right:.15em solid grey;
            white-space:nowrap;
            animation:typing 2.5s steps(22,end), blink .75s infinite;
        }

        @keyframes typing {
            from {width:0}
            to {width:22ch}
        }

        @keyframes blink {
            from,to {border-color:transparent}
            50% {border-color:grey}
        }
        </style>

        <div class="welcome-container">
        <div class="typewriter">
        Ready to Chat with Guru
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    for msg in st.session_state["message_history"]:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# ============================================================
# Chat Input
# ============================================================

userinput = st.chat_input("Type your message here...")


# ============================================================
# Chat Logic
# ============================================================

if userinput:

    current_thread = st.session_state["thread_id"]

    if current_thread not in st.session_state["chat_titles"]:

        title = generate_title(userinput)

        st.session_state["chat_titles"][current_thread] = title

    st.session_state["message_history"].append({
        "role": "user",
        "content": userinput
    })

    with st.chat_message("user"):
        st.write(userinput)

    CONFIG = {
        "configurable": {
            "thread_id": current_thread
        }
    }

    with st.chat_message("assistant"):

        ai_message = st.write_stream(

            message_chunk.content

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=userinput)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

        st.session_state["message_history"].append({
            "role": "assistant",
            "content": ai_message
        })

    st.rerun()