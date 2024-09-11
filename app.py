import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA # This library is hella sus
from langchain.llms import HuggingFaceHub
# from langchain.chains import create_history_aware_retriever
# from langchain_community.llms import HuggingFaceInference #what the fuck is this
from transformers import pipeline
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

def get_vectorstore(text_chunks):
    # embeddings=OpenAIEmbeddings()
    embeddings=HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore=FAISS.from_texts(texts=text_chunks,embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    model = pipeline("text-generation", model="google/flan-t5-xxl")
    llm = HuggingFaceInference(inference_client=model, model_name="google/flan-t5-xxl")
    llm.temperature = 0.5
    llm.max_length = 512
    memory=ConversationBufferMemory(memory_key='chat_history',return_messages=True)
    conversation_chain=RetrievalQA.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()

    st.set_page_config(page_title="Chat with multiple PDFs",page_icon=":books")


    if "conversation" not in st.session_state:
        st.session_state.conversation=None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None



    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs=st.file_uploader("Upload your PDFs here and Click on process",accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text=get_pdf_text(pdf_docs)

                text_chunks=get_text_chunks(raw_text)

                vectorstore=get_vectorstore(text_chunks)

                st.session_state.conversation=get_conversation_chain(vectorstore)
    



if __name__=='__main__':
    main()
