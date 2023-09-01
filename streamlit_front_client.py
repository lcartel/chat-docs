import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

# Sidebar contents
with st.sidebar:
    st.title('🤗💬 LLM Chat App')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
 
    ''')
    add_vertical_space(5)
    st.write('Made with ❤️ by [Leo Cartel](https://github.com/lcartel)')

def main():
    st.text_input('Selected pdf', 'Enduro_2_OM_EN-US.pdf', disabled=True)

if __name__ == '__main__':
    main()