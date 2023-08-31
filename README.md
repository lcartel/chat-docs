## Chat Doc is a tool that let your Company use your docs as a chatbot
## Tools used
- Chat GPT API
- LangChain
- [Gradio](https://www.gradio.app/)


# How to install
## Method 1 : Using anaconda
1. [Install Miniconda using the documentation](https://docs.conda.io/en/latest/miniconda.html)
2. Import the conda environment from *chat_doc_env_file.yml*
```bash
$> conda env create -n chat_docs_env --file chat_doc_env_file.yml
```
# Using your private_key
Complete the file *.env* with your open_ai key :
```env
OPENAI_API_KEY={VALUEOFYOURPUBLICKEY}
```