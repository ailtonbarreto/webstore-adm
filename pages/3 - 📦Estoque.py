import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



tab1, tab2 = st.tabs(["Consultar Estoque", "Adicionar Movimentação"])




@st.cache_data
def load_estoque():
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
      
        query = """ SELECT * FROM tembo.tb_mov_estoque;"""
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

df = load_estoque()


# -------------------------------------------------------------------------------------------------------
# PESQUISAR PRODUTO

with tab1:
    col1, col2  = st.columns(2)

    with col1:
        st.subheader("Pesquisa", anchor=False)
    with col2:
        st.subheader("Estoque", anchor=False)

    with col1:
        produto_filtro = st.text_input("Pesquisar pelo SKU",placeholder="Digite e tecle Enter")
        produto_filtro = produto_filtro.upper()

        if produto_filtro:
   
            df_produto = df.query('SKU == @produto_filtro')

            if not df_produto.empty:
                with col2:
                    df_qtd = df_produto.query('SKU == @produto_filtro')
                    df_qtd = df_qtd["QTD"].sum()
                    st.metric("",f'{df_qtd:,.0f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
            else:
                with col2:
                    st.metric("Nenhum produto encontrado.")

    if st.button("🔁 Atualizar"):
        st.cache_data.clear()
        st.rerun
        
        
# ---------------------------------------------------------------------------------------------------------
# estilizacao

style1 = """
    <style>
    [data-testid="stColumn"]
    {
    background-color: #ffffff;
    padding: 0.5vw 0.5vw;
    border-radius: 15px;
    text-align: center;
    box-shadow: 5px 3px 5px rgba(0, 0, 0, 0.3);
    }
    </style>
"""
st.markdown(style1, unsafe_allow_html=True)

style2 = """
    <style>
    [data-testid="stFullScreenFrame"]
    {
    display: flex;
    justify-content: center;
    }
    </style>
"""
st.markdown(style2, unsafe_allow_html=True)
