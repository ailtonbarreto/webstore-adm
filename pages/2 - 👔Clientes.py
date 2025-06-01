import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.subheader("Clientes",anchor=False)

tab1, tab2, tab3 = st.tabs(["Pesquisar Cliente", "Cadastrar Cliente", "Editar Cliente"])


# -------------------------------------------------------------------------------------------------------

@st.cache_data
def load_clientes():
    host = 'ep-long-salad-aczix9aa-pooler.sa-east-1.aws.neon.tech',
    database = 'webstore_b2b',
    user = 'webstore_b2b_owner',
    password = 'npg_iYEzyaTLg4f8',
    port = '5432'

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )        
      
        query = "SELECT * FROM publi.tb_cliente;"
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

df = load_clientes()

# -----------------------------------------------------------------------------------------------------


with tab1:

    col1, col2 = st.columns(2)

    with col1:

        filtro_cliente = st.selectbox("Pesuisar Cleinte",df["CLIENTE"].unique())

        df_resultado = df.query('CLIENTE == @filtro_cliente')
        
        st.dataframe(df_resultado,use_container_width=True,hide_index=True)