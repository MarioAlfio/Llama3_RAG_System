import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.blob_upload import save_file_blob_to_db, get_uploaded_files_metadata, get_file_blob_by_id
import streamlit as st
from etl.blob_upload import save_file_blob_to_db, get_uploaded_files_metadata, get_file_blob_by_id
import pandas as pd
import io

st.title("Upload e storico file su DB")

# --- UPLOAD NUOVO FILE ---
uploaded_file = st.file_uploader("Carica un file CSV/Excel", type=["csv", "xlsx"])
if uploaded_file is not None:
    file_bytes = uploaded_file.getbuffer()
    upload_id = save_file_blob_to_db(file_bytes, uploaded_file.name, user='utente1')
    st.success(f"File caricato e salvato su DB! ID: {upload_id}")

# --- STORICO E VISUALIZZAZIONE FILE ---
st.header("Storico file caricati su DB")
files = get_uploaded_files_metadata()
if files:
    for f in files:
        st.write(f"ID: {f['id']} | Nome: {f['filename']} | User: {f['user']} | Data: {f['upload_time']}")
        if st.button(f"Visualizza {f['filename']}", key=f"show_{f['id']}"):
            file_bytes, filename = get_file_blob_by_id(f['id'])
            if file_bytes:
                # Carica DataFrame in memoria
                if filename.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(file_bytes))
                else:
                    df = pd.read_excel(io.BytesIO(file_bytes))
                st.write(df.head())
            else:
                st.error("File non trovato nel DB.")
else:
    st.info("Nessun file caricato nel database.")