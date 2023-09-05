import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import openai
import os
import json
import langchain
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from PyPDF2 import PdfReader
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import pathlib
import logging, sys


PATH_DOCUMENTATIONS = "./documentations/examples/source_pdf/companies"
PATH_EMBEDDINGS = "./documentations/examples/embeddings/companies"
ENABLE_DEBUG = True

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
        temperature=0, 
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
        request_language = "fr",
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
        request_language = "en",
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
        request_language = "fr",
        type_of_object = ""
    }}

    User: How to reset my LG G2 TV ?
    Response:
    {{
        out_of_scope = False,
        brand_exists = True,
        model_exists = True,
        selected_brand = "lg",
        selected_model = "g2",
        request_language = "en",
        type_of_object = "tv"
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

def find_model_path(selected_brand, model, debug):
    try:
        #TO DO : Include examples with model number in 1 part and 3 part. E.g : C3, PSP

        selected_doc_path = []
        doc_base_path = PATH_DOCUMENTATIONS

        ## Checking outputs
        if not selected_brand in os.listdir(doc_base_path): return []
        model_split = model.split("_")
        if ((len(model_split) != 2) | (model_split[0].strip() == "") | (model_split[1].strip() == "")): return []

        for current_file_path in os.listdir(os.path.join(doc_base_path, selected_brand.lower())):
            if (
                (str(model_split[0]) in str(current_file_path.lower())) |
                (str(model_split[1]) in str(current_file_path.lower())) & 
                (".pdf" == str(os.path.splitext(current_file_path)[1]).lower())
            ):
                if (current_file_path.lower().index(model_split[0]) < current_file_path.lower().index(model_split[1])):
                    selected_doc_path.append(os.path.join(doc_base_path, selected_brand, current_file_path))
        return selected_doc_path

    except Exception as error:
        if debug: 
            print("An exception occurred:", type(error).__name__)
        return []

def has_embeddings(pdf_file, brand):
    return True if os.path.isfile(os.path.join(PATH_EMBEDDINGS,brand,pdf_file)) else False

def split_pdf_into_chunks(path_pdf):
    pdf_reader = PdfReader(path_pdf)

    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text()
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text=text)

    return chunks

def process_embeddings(chunks, pdf_file_name):
    store_name = pathlib.Path(pdf_file_name).stem
    embeddings = OpenAIEmbeddings()
    VectorStore = FAISS.from_texts(chunks, embedding=embeddings)    
    with open(os.path.join(PATH_EMBEDDINGS,store_name+".pickle"), "wb") as f:
        pickle.dump(VectorStore, f)

def handle_query(vector_store, query):
    docs = vector_store.similarity_search(query=query, k=3)
    llm = OpenAI(model_name='gpt-3.5-turbo')
    chain = load_qa_chain(llm=llm, chain_type="stuff")    
    return chain.run(input_documents=docs, question=query)

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
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try: 
                    dict_answer = json.loads(return_request_info(prompt))
                    if ENABLE_DEBUG:
                        logging.debug("dict_answer :", dict_answer)
                    if dict_answer["out_of_scope"]:
                        response = ("Please retry with a request about a specific product and documentation")
                    else:
                        selected_doc_path = find_model_path(dict_answer["selected_brand"], dict_answer["selected_model"], ENABLE_DEBUG)
                        if (len(selected_doc_path) == 0):
                            response = "We can't find the model and brand you provided in our database"
                        else:
                            #Check if embedding already exists
                            if not has_embeddings(selected_doc_path[0], dict_answer["selected_brand"]):
                                chunks = split_pdf_into_chunks(selected_doc_path[0])
                                process_embeddings(chunks, selected_doc_path[0])

                            #Get embeddings
                            with open(os.path.join(PATH_EMBEDDINGS,pathlib.Path(selected_doc_path[0]).stem+".pickle"), "rb") as f:
                                vector_store = pickle.load(f)                
                            
                            response = handle_query(vector_store, prompt)
                except Exception as error:
                    logging.debug("An exception occurred :", type(error).__name__)
                    response = "There is a problem on our side, please retry your question"    

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