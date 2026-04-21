from langgraph.graph import StateGraph , START , END 
from typing import TypedDict , Annotated
import os 
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from langchain_core.messages import BaseMessage   , HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3


# ====================================================================
                            # load modules
# ====================================================================
#load environment 
load_dotenv()
#check token 
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    print("Error: HUGGINGFACEHUB_API_TOKEN is not set in the .env file.")
else:
    print("Done")

#  Setup the Endpoint
repo_id = "meta-llama/Llama-3.1-8B-Instruct"

llm_H = HuggingFaceEndpoint(
    repo_id=repo_id,
    task="text-generation",
    max_new_tokens=512,
    temperature=0.7,
    huggingfacehub_api_token=token,
)

#  Wrap it in ChatHuggingFace (This handles the "conversational" format for you)
llm = ChatHuggingFace(llm=llm_H)
# ====================================================================
                            # Define Schema
# ====================================================================
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage] , add_messages]
# ====================================================================
                            # Function
# ====================================================================
#function 
def chat(state:ChatState):
    """
    Description:

    Parameters
    ----------
    :param state: INSERT DESCRIPTION
    :type state: ChatState

    .
    """
    #user query 
    messages =  state['messages']
    #llm 
    response = llm.invoke(messages)
    #response
    return {"messages": [response]}

# ====================================================================
                            # connection
# ====================================================================
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
# ====================================================================
                            # Checkpointer
# ====================================================================
#checkpointer 
checkpointer = SqliteSaver(conn = conn)
# ====================================================================
                            # define Graph
# ====================================================================
#Graph define 
graph  = StateGraph(ChatState)
# ====================================================================
                            # define Nodes
# ====================================================================
# nodes 
graph.add_node("chat",chat)
# ====================================================================
                            # define Edges
# ====================================================================
#edge
graph.add_edge(START,"chat")
graph.add_edge("chat",END)
# ====================================================================
                            # Compile Graph
# ====================================================================
chatbot = graph.compile(checkpointer=checkpointer)



def generate_chat_title(user_message):
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

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content.strip()


CONFIG = {"configurable": {"thread_id": "test_thread"}}
test = chatbot.invoke(
                {"messages": [HumanMessage(content="Hello, what is computer vision?")]},
                config = CONFIG,
            )

print(test)