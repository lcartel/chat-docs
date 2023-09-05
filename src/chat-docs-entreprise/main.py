import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from streamlit_tags import st_tags
import os
import requests
from bardapi import Bard, SESSION_HEADERS
import json 
import logging

USE_BARD_AUTOCOMPLETE=False
ENABLE_DEBUG=True
PATH_DOCUMENTATION="./documentations/uploads/source_pdf/companies"

# Sidebar contents
with st.sidebar:
    st.title('👨‍💻💬 LLM Chat Doc - Entreprise')
    st.markdown('''
    ## About
    This app allow you to turn your PDF files into a ready to use chatbot for your customers!
    To get started : 
    1. Upload your pdf file of choice
    2. Fill your *Company* name and the name of your *Product (Model)*
    3. Click *Save*
    ''')
    add_vertical_space(5)

def load_bard_credentials():
    session = requests.Session()

    token = os.getenv('BARD_API_Secure-1PSID')
    session.cookies.set("__Secure-1PSID", os.getenv('BARD_API_Secure-1PSID'))
    session.cookies.set( "__Secure-1PSIDCC", os.getenv('BARD_API_Secure-1PSIDCC'))
    session.cookies.set("__Secure-1PSIDTS", os.getenv('BARD_API_Secure-1PSIDTS'))
    session.headers = SESSION_HEADERS

    # bard_token = os.getenv('BARD_KEY')
    try: 
        return Bard(token=token, session=session)
    except Exception as error:
        if ENABLE_DEBUG:
            logging.debug("An exception occurred in loading bar credentials:", type(error).__name__)
        return Exception

def get_model_and_brand(bard, pdf_filename):
    bard_instructions = f"""
    You will act as a brand and model detector. If the brand is not included in the product name use your knowledge.
    I will pass you an name of a file and you will do your best to detect the brand and the model of the product.
    Only include one value for brand or product.
    I want your answer to be formated as a json like this:
    Response:
    {{
        brand = "",
        model = ""
    }}
    Don't include any explanation or other text than your json code.
    filename: ```{pdf_filename}```
    """
    try:
        answer_bard = bard.get_answer(bard_instructions)['content']    
        return json.loads(answer_bard.split("```")[1].replace("json\n",""))
    except Exception as error:
        logging.debug("An exception occurred:", type(error).__name__)
        return {}
    
def check_if_file_exists(folder, file_name):
    pass
def main():
    # Add a file input field for the user to select their PDF file
    
    uploaded_pdf = st.file_uploader("Upload a new pdf", type="pdf")
    if uploaded_pdf is not None:
        pdf_reader = PdfReader(uploaded_pdf, 'rb')
        dic_tag = {}
        if (USE_BARD_AUTOCOMPLETE):
            # We check for user credentials
            try:
                bard = load_bard_credentials()
                file_name = str(uploaded_pdf).split("name='")[1].split("',")[0]
                dic_tag = get_model_and_brand(bard, file_name)
            except Exception as error:
                if ENABLE_DEBUG:
                    logging.debug("An exception occurred:", type(error).__name__)
                st.warning('Impossible to autocomplete **brand** and **model** field. Please check your connection with *Bard*.', icon="⚠️")
 
        with st.form("my_form"):
            brand_name = st_tags(
                label='#### Brand :',
                text='Press ENTER to confirm the brand',
                value = dic_tag["brand"] if (USE_BARD_AUTOCOMPLETE & (len(dic_tag) !=0) ) else [],
                maxtags = 1,
                key='1')
            model_name = st_tags(
                label='#### Model :',
                text='Press ENTER to confirm the model',
                value=dic_tag["model"] if (USE_BARD_AUTOCOMPLETE & (len(dic_tag) !=0) ) else [],
                maxtags = 1,
                key='2')
        
            submitted = st.form_submit_button("Save")
            if submitted:
                if ( (len(brand_name) > 0) & (len(model_name) > 0)): 
                    if (brand_name[0] != "") & (model_name[0] != ""):
                        try:
                            os.mkdir(os.path.join(PATH_DOCUMENTATION,brand_name[0].lower()),mode=0o777)
                        except:
                            pass
                        #Save file

                        merger = PdfMerger()
 
                        merger.append(pdf_reader)

                        file_name = str(uploaded_pdf).split("name='")[1].split("',")[0]

                        merger.write(os.path.join(PATH_DOCUMENTATION,brand_name[0].lower(),file_name))
                        merger.close()

                        PdfWriter(pdf_reader)
                        st.success('Your file has been saved !', icon="✅")
                else:
                    st.warning('Please complete all tags', icon="⚠️")

if __name__ == '__main__':
    main()