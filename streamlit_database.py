import streamlit as st
from langgraph_tools_backend import chatbot, retrieve_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid


#*********************** utility function ***************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
        
def old_chat(thread_id):
    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )

    old_message = state.values.get('messages', [])

    return old_message
        
    

# ****************************** session setup ***************************************

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']},
          "metadata":{
              "thread_id": st.session_state["thread_id"]
          },
          "run_name": "chat_turn"
          }

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_threads()
    
add_thread(st.session_state['thread_id'])

# *****************************SIDEBAR UI ***********************************************
st.sidebar.title('LNAGGRAPH CHATBOT')


if st.sidebar.button('New Chat'):
    reset_chat()
    
    
    
st.sidebar.header('My Conversation')


for thread_id in st.session_state['chat_thread']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = old_chat(thread_id)       

        temp_messages = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role='assistant'
            temp_messages.append({'role':role, 'content': msg.content})
            
        st.session_state['message_history'] = temp_messages


# ******************* functionality ***********************************
    
for message in st.session_state['message_history']:
    
    with st.chat_message(message['role']):
        st.text(message['content'])
        

user_input = st.chat_input('Type here')

if user_input:
    
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    with st.chat_message('assistant'):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content
                    
        ai_message = st.write_stream(ai_only_stream)
        
        
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    