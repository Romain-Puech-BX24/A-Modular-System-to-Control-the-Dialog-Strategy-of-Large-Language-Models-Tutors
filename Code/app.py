# By Romain Puech, Feb 2024

from openai import AzureOpenAI
import streamlit as st
from streamlit_chat import message
import json
import copy
import itertools
import Tutor, Student
import Intermediary
from utils import print_logs,generate_messages
from get_key import get_client
from problems import create_msgs,get_pb_sol
from taxonomy import Intent



####################################
############# Settings #############

### global vars
topic = "consistency"
pb,sol = get_pb_sol("consistency")
if 'topic' not in st.session_state:
    st.session_state['topic'] = topic
if 'pb' not in st.session_state:
    st.session_state['pb'] = pb
if 'sol' not in st.session_state:
    st.session_state['sol'] = sol


model_name = "GPT-4" 
model = "myGPT35" 

### Azure OpenAI API key
client = get_client()

### Session state vars
if 'tutor' not in st.session_state:
    st.session_state['tutor'] = ["Hello! Can you walk me through your solution?"]
if 'student' not in st.session_state:
    st.session_state['student'] = []
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0
if 'tellprompt' not in st.session_state:
    st.session_state['tellprompt'] = False
if 'Student' not in st.session_state:
    st.session_state['Student'] = Student.Student(client, pb = st.session_state['pb'], model = model)
if 'Tutor' not in st.session_state:
    st.session_state['Tutor'] = Tutor.Tutor(client, pb=st.session_state['pb'], sol=st.session_state['sol'], model = model)
if 'intent' not in st.session_state:
    st.session_state['intent'] = []
if 'assessment' not in st.session_state:
    st.session_state['assessment'] = []



##############################################
########### Chat History Functions ###########
def clear_chat_history():
    st.session_state['tutor'] = ["Hello! Can you walk me through your solution?"]
    st.session_state['student'] = []
    st.session_state['intent'] = []
    st.session_state['assessment'] = []
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    st.session_state['Student'] = Student.Student(client, pb = st.session_state['pb'], model = model)
    st.session_state['Tutor'] = Tutor.Tutor(client, pb=st.session_state['pb'], sol=st.session_state['sol'], model = model)
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

def generate_dict_history():
    return {
        "student": st.session_state["student"],
        "tutor": st.session_state["tutor"],
        "intents": [[intent.name for intent in intent_list] for intent_list in st.session_state["intent"]],
        "assessments": st.session_state["assessment"],
        "total_cost": st.session_state["total_cost"],
        "pb": st.session_state['pb'],
        "sol": st.session_state['sol']
    }

def save_chat_history(chat_data, filename="chat_history.json"):
    with open(filename, 'w') as f:
        json.dump(chat_data, f, indent=4)

def load_chat_history(filename="chat_history.json"):
    with open(filename, 'r') as f:
        return json.load(f)
    
def set_chat_history_2(chat_history):
    st.session_state['tutor'] = chat_history["tutor"]
    st.session_state['student'] = chat_history["student"]
    st.session_state['intent'] = [[Intent[intent_name] for intent_name in intent_list] for intent_list in chat_history["intents"]]
    st.session_state['assessment'] = chat_history["assessments"]
    st.session_state['pb'] = chat_history["pb"]
    st.session_state['sol'] = chat_history["sol"]
    st.session_state['Tutor'] = Tutor.Tutor(client, pb=st.session_state['pb'], sol=st.session_state['sol'], model = model)
    st.session_state['Student'] = Student.Student(client, pb = st.session_state['pb'], model = model)
    st.session_state['model_name'] = [ 'GPT4' for c in chat_history["tutor"]]
    st.session_state['total_tokens'] = [0 for c in chat_history["tutor"]]
    st.session_state['cost'] = [ 0 for c in chat_history["tutor"]]
    st.session_state['total_cost'] = chat_history["total_cost"]
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
    

############# UI #############
    
#### Title
st.set_page_config(page_title="PFT1", page_icon=":book:")
st.markdown("<h1 style='text-align: center;'>Productive Failure AI Maths Tutor</h1>", unsafe_allow_html=True)

#### Sidebar
st.sidebar.title("Infos")
model_name = st.sidebar.radio("Choose a model:", ("GPT-4","GPT-3.5"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")
save_chat_button = st.sidebar.button("Save Chat History", key="save")
file_name = st.sidebar.text_input("Enter the chat JSON filename")
load_chat_button = st.sidebar.button("Load Chat History", key="load")
autoplay_button = st.sidebar.button("Autoplay", key="auto")
print_msg_button = st.sidebar.button("log", key="log")


### Main containers

response_container = st.container()
container = st.container()

# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "myGPT35"
else:
    model = "myGPT4"


############# UX #############

### Clear chat
if clear_button:
    clear_chat_history()

### Save chat
if save_chat_button:   
    chat_history = generate_dict_history()
    if file_name:
        if not file_name.endswith('.json'):
            file_name += '.json'
        save_chat_history(chat_data=chat_history,filename=file_name)
    else:
        save_chat_history(chat_data=chat_history)
    # Notify the user
    st.sidebar.success("Chat history saved!")

### Load chat
if load_chat_button:
    if file_name:
        # Add the file extension if not present
        if not file_name.endswith('.json'):
            file_name += '.json'
        chat_history = load_chat_history(file_name)
    else:
        chat_history = load_chat_history()  # Load default
    response_container.empty()
    set_chat_history_2(chat_history)
    #reset_messages()  # Reset messages for the chat UI
    

### print log
if print_msg_button:
    print_logs(generate_messages(st.session_state["student"],st.session_state["tutor"],'',"tutor"))



############# Main Loop #############
cum_total_tokens = 0
cum_cost = 0


with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input or autoplay_button:
        if autoplay_button:
            student_utterance, student_total_tokens, student_prompt_tokens, student_completion_tokens = st.session_state['Student'].get_response(st.session_state['student'], st.session_state['tutor'])
        else:
            student_utterance, student_total_tokens, student_prompt_tokens, student_completion_tokens = user_input,0,0,0
        st.session_state['student'].append(student_utterance)
        output, tutor_total_tokens, tutor_prompt_tokens, tutor_completion_tokens, intent, assessment = st.session_state['Tutor'].get_response(st.session_state['student'], st.session_state['tutor'])
        st.session_state['tutor'].append(output)
        st.session_state['intent'].append(intent)
        st.session_state['assessment'].append(assessment)
        #st.session_state['model_name'].append(model_name)
        total_tokens = student_total_tokens + tutor_total_tokens
        prompt_tokens = tutor_prompt_tokens + student_prompt_tokens
        completion_tokens = tutor_completion_tokens + student_completion_tokens
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost


if st.session_state['tutor'] or st.session_state['student']:
    with response_container:
        for i,(msg_s,msg_t) in enumerate(itertools.zip_longest(st.session_state['student'],st.session_state['tutor'])):
            if msg_t:
                message(msg_t, key=str(i),logo="https://openai.com/favicon.ico")
            if msg_s:
                message(msg_s, is_user=True, key=str(i) + '_user')
            #st.write(
            #    f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            
            
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

