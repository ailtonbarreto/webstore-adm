import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------
# DATABASE POSTGRES NA NUVEM

@st.cache_data
def load_data():
    host = 'gluttonously-bountiful-sloth.data-1.use1.tembo.io'
    database = 'postgres'
    user = 'postgres'
    password = 'MeSaIkkB57YSOgLO'
    port = '5432'

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )        
        # query = "SELECT * FROM tembo.tb_integracao;"
        
        query = "SELECT * FROM tembo.tb_integracao;"
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

df = load_data()


json_result = df.to_json(orient='records', lines=True)

st.dataframe(df,hide_index=True,use_container_width=True)