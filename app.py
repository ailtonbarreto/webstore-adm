import streamlit as st
import pandas as pd
import gspread as sg
from gspread import Worksheet

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="🟢", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

st.title("Ativar e inativar produtos",anchor=False)
st.divider()

col1, col2 = st.columns(2)

# ----------------------------------------------------------------------------------------
# Dados Saídas

gc = sg.service_account("key.json")
url = 'https://docs.google.com/spreadsheets/d/1FZblAsihwNUfUVNDvdRQQ3SHx1PeOficVXcPLsQep3s/edit?usp=sharing'



sh = gc.open_by_url(url)   
ws = sh.get_worksheet(0)   
planilha = ws.get_all_values()   
df = pd.DataFrame(planilha[1:], columns=planilha[0])
df["PARENT"] = df["PARENT"].astype(int)
# df.index = df["PARENT"]

# df["IMAGEM"] = df["IMAGEM"].apply(lambda img_url: f'<img src="{img_url}" style="width:100px;"/>')

df = df.drop(columns="IMAGEM")

# -------------------------------------------------------------------------------------------
with col1:
    produto = st.number_input("PARENT",step=1)
with col2:
    valor_status = st.selectbox("Status",["Ativo","Inativo"])  

df_filtered = df.query('PARENT == @produto')


if valor_status == "Ativo":
    status = 1
else:
    status = 0


index = df_filtered.index[0] + 2

if produto == 0:
    df_filtered = st.dataframe(df,use_container_width=True,hide_index=False)
else:
   st.dataframe(df_filtered,use_container_width=True,hide_index=False)
   
   
if st.button("SALVAR EDIÇÃO"):
    ws1: Worksheet = sh.get_worksheet(0)
    ws1.update_cell(int(index), 6, status)
    st.success("Edição salva!")

