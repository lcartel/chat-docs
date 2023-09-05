<h1 align="center" style="display: block; font-size: 2.5em; font-weight: bold; margin-block-start: 1em; margin-block-end: 1em;">
<img align="center" src="./img/logo_banner.png" alt="Chat Doc Logo" style="width:100%;height:100%"/>
  <br /><br /><strong>CHAT DOC</strong>
</h1>

The platform offer double benefits:
- On the entreprise side: It allows any companies to upload their pdf and tag them to put it available to their customer in the chatbot.
- On the client side: It allows clients to ask questions about their favorite products without spending further time in the documentation.

The following tools have been used:
- [Open AI API](https://platform.openai.com/docs/api-reference)
- [LangChain 🦜️🔗](https://python.langchain.com/docs/get_started/introduction.html)
- [Streamlit](https://streamlit.io/)

## Install
### 1. Install package into anaconda
1. [Install Miniconda using the documentation](https://docs.conda.io/en/latest/miniconda.html)
2. Import the conda environment from *chat_doc_env_file.yml*
```bash
$> conda env create -n chat_doc_env --file requirements.txt
$> conda activate chat_doc_env
```
### 2. Configure your private key
Create an *.env* file at the root of the repository with your open ai api key:

```javascript
OPENAI_API_KEY={VALUEOFYOURPUBLICKEY}
```

To create a new API key follow the instructions bellow:
1. Go to OpenAI's Platform website at [platform.openai.com](platform.openai.com) and sign in with an OpenAI account.
2. Click your profile icon at the top-right corner of the page and select "View API Keys."
3. Click "Create New Secret Key" to generate a new API key.

## Run locally using command line
Please not that all the command bellow are run from the root folder.
### Running the *client* server
```bash
$> streamlit run src/chat-docs-client/main.py
```

### Running the *entreprise* server
```bash
$> streamlit run src/chat-docs-entreprise/main.py
```

### Running the *debug mode* 
Activate the variable *ENABLE_DEBUG=TRUE*
```bash
$> streamlit run src/[youfile]/main.py --logger.level debug
```

## Run locally VS Code (Debug mode)
A *launch.json* file is already present in the repository. 
You should be able to run and debug any file from their main.py by pressing F5 on your keyboard.


## Screenshots


## Limitations
- The chatbot has no "memory" you can't ask it about previous interaction.
- The chatbot only answer about it's own knowledge. It can't answer any question outside of the scope of the PDF provided