import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.image("header.png", width=1300)


tab1, tab2 = st.tabs(["Visão Geral", "Cadastrar Produto"])

with tab1:
    st.write("🚧Em construção")

# -------------------------------------------------------------------------------------------------------
# SELECT CARREGAR DATAFRAME

consulta = """
SELECT * FROM tembo.tb_produtoç"
"""

# -------------------------------------------------------------------------------------------------------

@st.cache_data
def load_produtos():
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
      
        query = consulta
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

df = load_produtos()


with tab1:
    st.dataframe(df,use_container_width=True)

# ----------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
with tab2:
    parent = st.number_input("Parent", step=1)
    parent = int(parent)

    sku = st.text_input("SKU")

    descricao_parent = st.text_input("Descrição Parent")
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")
    url = st.text_input("URL da Imagem")
    

    vr_unit = st.number_input("Valor Unit", format="%.2f")
    vr_unit = float(vr_unit)

    # Função de inserção
    def insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent):
        try:
 
            conn = psycopg2.connect(
                host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                database='postgres',
                user='postgres',
                password='MeSaIkkB57YSOgLO',
                port='5432'
            )


            insert_query = """
            INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "DESCRICAO_PARENT","IMAGEM")
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

  
            cursor = conn.cursor()
            cursor.execute(insert_query, (parent, sku, descricao, categoria, vr_unit, descricao_parent,url))
            conn.commit()

            st.write("Dados inseridos com sucesso!")
        except Exception as e:
            st.write(f"Erro ao inserir dados: {e}")
        finally:
            if conn:
                conn.close()

 
    if st.button("💾"):
 
        if sku and descricao and categoria and vr_unit > 0:
            insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent)
        else:
            st.write("Por favor, preencha todos os campos necessários.")

