import streamlit as st
import random
import time
from streamlit_extras.add_vertical_space import add_vertical_space
import openai
import os
import json
import langchain
import sys
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai.api_key  = os.getenv('OPENAI_API_KEY')


# Sidebar contents
with st.sidebar:
    st.title('🦉💬 LLM Chat Doc - User')
    st.markdown('''
    ## About
    This app allow you to ASK your questions about your favorite objects.
    To get started ask a specific question about an object or a brand to our chatbot.
    ''')
    add_vertical_space(5)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def return_request_info(user_prompt):

    user_prompt_cropped=user_prompt[:300]

    expected_examples = f"""
    User: I want the documentation of the marcel galaxy S21
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = samsung,
        selected_model = galaxy_s21,
        request_language = en,
        type_of_object = smartphone
    }}

    User: What is the waranty of the Apple Ibode 10
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = apple,
        selected_model = iphone_10,
        request_language = en,
        type_of_object = smartphone
    }}

    User: What is the waranty of the Apple Ibode X
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = apple,
        selected_model = iphone_10,
        request_language = en,
        type_of_object = smartphone
    }}

    User: Comment appairer mon sony xm5
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = sony,
        selected_model = wh-1000xm5,
        request_language = fr,
        type_of_object = car
    }}

    User: Comment reparer le feu arrière de ma citroen C40
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = citroen,
        selected_model = c4,
        request_language = fr,
        type_of_object = car
    }}

    User: Qui est le 5eme president des etats unis ?
    Response:
    {{
        out_of_scope = True,
        brand_exists = False,
        model_exists = False,
        selected_brand = "",
        selected_model = "",
        request_language = "",
        type_of_object = ""
    }}

    User: How much is 8 times 19 ?
    Response:
    {{
        out_of_scope = True,
        brand_exists = False,
        model_exists = False,
        selected_brand = "",
        selected_model = "",
        request_language = "",
        type_of_object = "",
    }}

    User: Qui a créer la renault 4CV ?
    Response:
    {{
        out_of_scope = True,
        brand_exists = False,
        model_exists = False,
        selected_brand = "",
        selected_model = "",
        request_language = "",
        type_of_object = ""
    }}


    """
    chat_instruction_if_no_brand_no_model = f"""
    An user will ask you for a specific question about a product brand and a model. \
    Your task is to determine the brand and the model that the user is refering too. \
    If you don't know the brand the user is refering too set the value of "brand_exists" key to False (using the same case), set the value of "model_exists" to False and all the other keys with a blank string and return the output without any more calculations. \
    If you don't see any brand in the prompt try to find it \
    It the model doesn't exists set the "model_exists" key to False (using the same case) but set the right value to brand. \
    You will also identify the language of the request as the key "request_language". \
    Also determine the type of object and put your result in the key "type_of_object". For example it could be smartphone, camera, car, etc.. \ 
    If the value doesn't concern any information about a product set the value of out_of_scope to True.

    I want your output formated as a json string with the following format: \
    {{
        out_of_scope = [Boolean],
        brand_exists = [Boolean], 
        model_exists = [Boolean], 
        selected_brand = [string],
        selected_model = [string],
        request_language = [string],
        type_of_object = [string]
    }}

    The boolean values (out_of_scope, brand_exists and model_exists value) will be in formated as camelcase, to respect python convention to boolean values.
    All other values should be in lowercase.

    Here are some example of answers:
    ```{expected_examples}```

    The user demand is delimited into tripple backtick
    ```{user_prompt_cropped}```
    """

    return get_completion(chat_instruction_if_no_brand_no_model)

def convert_response_to_dict(response):
    # Convert JSON String to Python


def main():
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter a question about a specific BRAND and MODEL"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        dict_answer = return_request_info(prompt)
        if dict_answer["out_of_scope"]:
            response = ("Please retry with a request about a specific product and documentation")
        else:
            #Step 1: Find the pdf using path. If not answer "Sorry we don't have this kind of info"
            #Step 2: Try to find embeddings. If not compute embeddings.
            #Step 3: Answer using embeddings.

            pass
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                assistant_response = response
                message_placeholder = st.empty()
                placeholder = st.empty()
                full_response = ""
                for item in assistant_response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == '__main__':
    main()