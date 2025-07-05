import streamlit as st
import requests
import pandas as pd
import json

ETL_API_URL = "http://etl:8001"
EDA_API_URL = "http://eda:8002/eda"

st.title("Frontend EDA: Carica, Visualizza, Elimina, Analizza")

# 1. Upload file
st.header("Carica un file CSV/XLSX")
uploaded_file = st.file_uploader("Scegli un file", type=["csv", "xlsx"])
if uploaded_file is not None:
    file_bytes = uploaded_file.getbuffer()
    files = {"file": (uploaded_file.name, file_bytes)}
    try:
        resp = requests.post(f"{ETL_API_URL}/upload/", files=files)
        if resp.status_code == 200:
            upload_id = resp.json()["upload_id"]
            st.success(f"File caricato! ID: {upload_id}")
            st.session_state["last_upload_id"] = upload_id
        else:
            st.error(f"Errore upload: {resp.text}")
    except Exception as e:
        st.error(f"Errore durante l'upload: {e}")

# 2. Storico file caricati con elimina
st.header("Storico file caricati")
try:
    resp = requests.get(f"{ETL_API_URL}/files/")
    if resp.status_code == 200:
        files = resp.json()
        for f in files:
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"ID: {f['id']} | Nome: {f['filename']} | User: {f['user']} | Data: {f['upload_time']}")
            with col2:
                if st.button("Elimina", key=f"del_{f['id']}"):
                    del_resp = requests.delete(f"{ETL_API_URL}/files/{f['id']}")
                    if del_resp.status_code == 200:
                        st.success("File eliminato!")
                        st.experimental_rerun()
                    else:
                        st.error("Errore durante l'eliminazione")
    else:
        st.info("Nessun file caricato nel database.")
except Exception as e:
    st.info(f"Impossibile recuperare lo storico file: {e}")

# 3. Esecuzione EDA
st.header("Esegui EDA su un file caricato")
selected_upload_id = st.text_input("ID file su cui eseguire EDA:", value=st.session_state.get("last_upload_id", ""))
if st.button("Esegui EDA", key="run_eda") and selected_upload_id:
    try:
        eda_resp = requests.post(f"{EDA_API_URL}/run_eda/{selected_upload_id}")
        if eda_resp.status_code == 200:
            eda_json = eda_resp.json()["eda_json"] if "eda_json" in eda_resp.json() else eda_resp.json()
            st.session_state["eda_result"] = eda_json
            st.success("EDA completata!")
        else:
            st.error(f"Errore durante l'EDA: {eda_resp.text}")
    except Exception as e:
        st.error(f"Errore durante l'esecuzione EDA: {e}")

# 4. Visualizza risultati EDA
if "eda_result" in st.session_state:
    st.header("Risultati EDA")
    try:
        eda = st.session_state["eda_result"]
        if isinstance(eda, str):
            eda = json.loads(eda)
        st.subheader("Colonne numeriche")
        st.write(eda.get("numeric_columns", []))
        st.subheader("Colonne categoriche")
        st.write(eda.get("categorical_columns", []))
        st.subheader("Colonne data")
        st.write(eda.get("date_columns", []))
        st.subheader("Describe (statistiche numeriche)")
        st.write(eda.get("describe", {}))
    except Exception as e:
        st.error(f"Errore nella visualizzazione EDA: {e}") 