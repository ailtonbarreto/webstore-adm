import streamlit as st
import pandas as pd
import gspread as sg
from gspread import Worksheet

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="🟢", layout="wide")

# with open("style.css") as f:
#     st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)


st.divider()

# ----------------------------------------------------------------------------------------
# Dados Saídas

gc = sg.service_account("key.json")
url = 'https://docs.google.com/spreadsheets/d/1FZblAsihwNUfUVNDvdRQQ3SHx1PeOficVXcPLsQep3s/edit?usp=sharing'



sh = gc.open_by_url(url)   
ws = sh.get_worksheet(0)   
planilha = ws.get_all_values()   
df = pd.DataFrame(planilha[1:], columns=planilha[0])


# df = load_data(url)

# df = df.drop(columns="IMAGEM")



# dfeditar = df




st.dataframe(df,use_container_width=True,hide_index=True)