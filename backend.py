from langgraph.graph import StateGraph , START , END
from typing import TypedDict , Annotated
import os 
from dotenv import load_dotenv 
from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from langchain_core.messages import BaseMessage , HumanMessage 
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
    messages : Annotated[list[BaseMessage],add_messages]

def chat(state:ChatState):
    #user query 
    messages = state['messages']
    #llm 
    response = llm.invoke({"messages": messages})
    #response
    return {"messages":[response]}
    
# Connection with SQLite for checkpointing
conn = sqlite3.connnect(database="chatbot_history.db",check_same_thread=False)

#checkpointer 
checkpointer = SqliteSaver(conn=conn)


# Graph 
graph = StateGraph(ChatState)


# Nodes 
graph.add_node("chat" ,chat )
# Edges
graph.add_edge(START , "chat")
graph.add_edge("chat" , END)


# Compile 
chatbot = graph.compile()

def retrieve_all_threads():
    add_threads = set()
    for cp in checkpointer.list(None):
        add_threads.add(cp.config['config']['thread_id'])

    return list(add_threads)