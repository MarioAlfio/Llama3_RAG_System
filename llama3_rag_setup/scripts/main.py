import os
import streamlit as st
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.generators.ollama import OllamaGenerator
from loguru import logger

# Logging
logger.add("logs/app.log", rotation="10 MB")

# Sicurezza semplice: password da variabile ambiente
PASSWORD = os.getenv("STREAMLIT_PASSWORD", "changeme")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.title("Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Login effettuato!")
        else:
            st.error("Password errata")

if not st.session_state["authenticated"]:
    login()
    st.stop()

st.title("RAG con Llama3:8b (Ollama + Haystack)")

# Carica documenti di esempio (puoi sostituire con i tuoi)
docs = [
    Document(content="Super Mario was an important politician"),
    Document(content="Mario owns several castles and uses them to conduct important political business"),
    Document(content="Super Mario was a successful military leader who fought off several invasion attempts by his arch rival - Bowser"),
]

# Setup pipeline Haystack
document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

template = """
Given only the following information, answer the question.
Ignore your own knowledge.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}?
"""

pipe = Pipeline()
pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OllamaGenerator(model="llama3:8b", url="http://ollama:11434"))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

# Interfaccia Streamlit
query = st.text_input("Fai una domanda sui documenti caricati:")

if st.button("Chiedi") and query:
    logger.info(f"Domanda utente: {query}")
    response = pipe.run({"prompt_builder": {"query": query}, "retriever": {"query": query}})
    answer = response["llm"]["replies"][0]
    st.write("**Risposta:**", answer)
    logger.info(f"Risposta: {answer}")