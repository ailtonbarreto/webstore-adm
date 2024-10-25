import streamlit as st
import pandas as pd
import gspread as sg
from gspread import Worksheet

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="🟢", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

st.title("Ativar e inativar produtos",anchor=False)
st.divider()

# col1, col2 = st.columns(2)

# ----------------------------------------------------------------------------------------
# Dados Saídas

gc = sg.service_account("key.json")
url = 'https://docs.google.com/spreadsheets/d/1FZblAsihwNUfUVNDvdRQQ3SHx1PeOficVXcPLsQep3s/edit?usp=sharing'



# sh = gc.open_by_url(url)   
# ws = sh.get_worksheet(0)   
# planilha = ws.get_all_values()   
# df = pd.DataFrame(planilha[1:], columns=planilha[0])
# df["PARENT"] = df["PARENT"].astype(int)
# # df.index = df["PARENT"]

# # df["IMAGEM"] = df["IMAGEM"].apply(lambda img_url: f'<img src="{img_url}" style="width:100px;"/>')

# df = df.drop(columns="IMAGEM")

# # -------------------------------------------------------------------------------------------
# with col1:
#     produto = st.number_input("PARENT",step=1)
# with col2:
#     valor_status = st.selectbox("Status",["Ativo","Inativo"])  

# df_filtered = df.query('PARENT == @produto')


# if valor_status == "Ativo":
#     status = 1
# else:
#     status = 0


# index = df_filtered.index[0] + 2

# if produto == 0:
#     df_filtered = st.dataframe(df,use_container_width=True,hide_index=False)
# else:
#    st.dataframe(df_filtered,use_container_width=True,hide_index=False)
   
   
# if st.button("SALVAR EDIÇÃO"):
#     ws1: Worksheet = sh.get_worksheet(0)
#     ws1.update_cell(int(index), 6, status)
#     st.success("Edição salva!")

import psycopg2
from psycopg2 import sql

# Defina suas credenciais e informações de conexão
host = 'gluttonously-bountiful-sloth.data-1.use1.tembo.io'  # ex: 'host-do-seu-banco-de-dados.com'
database = 'postgres'
user = 'postgres'
password = 'MeSaIkkB57YSOgLO'
port = '5432'  # Porta padrão do PostgreSQL

# Estabeleça a conexão
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    st.write("Conexão bem-sucedida!")
    
    query = "SELECT * FROM tembo.tb_integracao;"
    df = pd.read_sql_query(query, conn)
except Exception as e:
    st.write(f"Erro ao conectar: {e}")

# Feche a conexão ao terminar
if conn:
    conn.close()


st.dataframe(df)