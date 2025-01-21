import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain    #deprecated
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.llms import HuggingFaceHub #deprecated
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain.chains import create_history_aware_retriever 
# from langchain_community.llms import HuggingFaceInference    
from dotenv import load_dotenv
from htmltemplates import css,bot_template,user_template
import sys

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader=PdfReader(pdf)
        for page in pdf_reader.pages:
            text+=page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter=CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len 
    )
    chunks=text_splitter.split_text(text)
    return chunks

# def get_vectorstore(text_chunks):
#     # embeddings=OpenAIEmbeddings()
#     embeddings=HuggingFaceInstructEmbeddings(model_name="paraphrase-MiniLM-L6-v2")
#     vectorstore=FAISS.from_texts(texts=text_chunks,embedding=embeddings)
#     return vectorstore

def get_vectorstore(text_chunks):
    embeddings = SentenceTransformerEmbeddings(model_name="paraphrase-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.5, "max_length": 512})

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    
    retrieval_chain = create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)
    
    return retrieval_chain

def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("Please upload and process PDFs before asking questions.")
        return

    response = st.session_state.conversation.invoke({"input": user_question})
    st.session_state.chat_history.append(("Human", user_question))
    st.session_state.chat_history.append(("AI", response['answer']))

    for role, message in st.session_state.chat_history:
        if role == "Human":
            st.write(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)

def main():
    load_dotenv()

    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs here and Click on process", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.success("Processing complete! You can now ask questions about your documents.")

if __name__ == '__main__':
    main()