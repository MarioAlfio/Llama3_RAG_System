import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
import pandas as pd
import io
import json
from pathlib import Path
import requests
from app.agent import EDAChatAgent
from app.utils import get_eda_json_from_service, upload_file_to_etl
from app.config import EDA_SERVICE_URL, OPENAI_API_KEY

# 1. Login utente
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Credenziali mancanti")
    st.stop()

# Logout
if st.button("Logout"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()

# 2. Inserimento chiave OpenAI
openai_key = st.text_input("Inserisci la tua OpenAI API Key:", type="password", value=OPENAI_API_KEY)
if not openai_key:
    st.warning("Inserisci la tua OpenAI API Key per usare il chatbot.")
    st.stop()

# Istanzia l'agente una sola volta in session_state
if "eda_agent" not in st.session_state or st.session_state.get("eda_agent_api_key") != openai_key:
    st.session_state["eda_agent"] = EDAChatAgent(api_key=openai_key)
    st.session_state["eda_agent_api_key"] = openai_key
agent = st.session_state["eda_agent"]

EDA_API_URL = "http://eda:8002/eda"

st.title("Chatbot sui tuoi dati EDA")

# 3. Selezione file EDA disponibile
st.header("Seleziona un file EDA")
try:
    files_resp = requests.get("http://etl:8001/files/")
    if files_resp.status_code == 200:
        files = files_resp.json()
        if not files:
            st.warning("Nessun file disponibile.")
            st.stop()
        file_options = {f"{f['filename']} (ID: {f['id']})": f['id'] for f in files}
        selected_label = st.selectbox("Scegli un file:", list(file_options.keys()))
        selected_upload_id = file_options[selected_label]
    else:
        st.warning("Nessun file disponibile.")
        st.stop()
except Exception as e:
    st.error(f"Errore nel recupero file: {e}")
    st.stop()

# 4. Recupera e mostra anteprima JSON EDA
st.header("Anteprima JSON EDA")
eda_json = None
if selected_upload_id:
    try:
        eda_resp = requests.post(f"http://eda:8002/eda/run_eda/{selected_upload_id}")
        if eda_resp.status_code == 200:
            eda_json = eda_resp.json()["eda_json"] if "eda_json" in eda_resp.json() else eda_resp.json()
            if isinstance(eda_json, str):
                eda_json = json.loads(eda_json)
            st.json(eda_json, expanded=False)
            # Indicizza l'EDA solo se cambia file selezionato
            if st.session_state.get("last_indexed_id") != selected_upload_id:
                agent.index_eda(eda_json, selected_upload_id)
                st.session_state["last_indexed_id"] = selected_upload_id
        else:
            st.error(f"Errore durante l'EDA: {eda_resp.text}")
            st.stop()
    except Exception as e:
        st.error(f"Errore durante l'esecuzione EDA: {e}")
        st.stop()
else:
    st.info("Seleziona un file per vedere l'EDA.")
    st.stop()

# 5. Chatbot
st.header("Chatbot sui dati EDA selezionati")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

question = st.text_input("Fai una domanda sui dati:", key="chat_input")
if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    try:
        answer = agent.answer(question)
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Errore durante la risposta del chatbot: {e}")

st.write(st.session_state) 