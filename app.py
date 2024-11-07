import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
    
    
card1, card2, card3, card4, card5, card6, card7 = st.columns([2,2,2,2,2,1,1])

# -------------------------------------------------------------------------------------------------------
# DATABASE POSTGRES NA NUVEM

consulta = """
SELECT 
    tembo.tb_venda."PEDIDO", 
    tembo.tb_venda."EMISSAO", 
    tembo.tb_venda."PARENT", 
    tembo.tb_venda."QTD",
    tembo.tb_venda."VR_UNIT",
    tembo.tb_venda."STATUS",
    tembo.tb_venda."SKU_CLIENTE", 
    tembo.tb_cliente."CLIENTE", 
    tembo.tb_produto."DESCRICAO"
FROM tembo.tb_venda
JOIN tembo.tb_cliente ON tembo.tb_venda."SKU_CLIENTE" = tembo.tb_cliente."SKU_CLIENTE"
JOIN tembo.tb_produto ON tembo.tb_venda."PARENT" = tembo.tb_produto."PARENT";
"""



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
      
        query = consulta
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

# ----------------------------------------------------------------------------------
# ETL
df = load_data()
df["data"] = pd.to_datetime(df["EMISSAO"])
df["Ano"] = df["data"].dt.year
df["Mês"] = df["data"].dt.month

def determinar_mês(valor):
    meses = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez"
    }
    return meses.get(valor)


df["Mês"] = df["Mês"].apply(determinar_mês)


# ----------------------------------------------------------------------------------
# filtros

with card6:
    filtro_inicio = st.date_input("Início",pd.to_datetime("2024-01-01").date(),format= "DD/MM/YYYY")
    
with card7:
    filtro_fim = st.date_input("Fim","today",format= "DD/MM/YYYY")

df_filtrado = df.query('@filtro_inicio <= `EMISSAO` <= @filtro_fim')

df_filtrado["TOTAL"] = df_filtrado["QTD"] * df_filtrado["VR_UNIT"]


# ----------------------------------------------------------------------------------
# kpis

qtd_pedidos = df_filtrado["PEDIDO"].unique().shape[0]

total = df_filtrado["TOTAL"].sum()

ticket_medio = total / qtd_pedidos

qtd_aguardando_pagamento = (df_filtrado["STATUS"] =="AGUARDANDO PAGAMENTO").unique().sum()


qtd_pedido_concluido = df_filtrado.query('STATUS == "CONCLUIDO"')
qtd_pedido_concluido = qtd_pedido_concluido["PEDIDO"].unique().shape[0]

qtd_pedido_planejados = df_filtrado.query('STATUS == "PLANEJADO"')
qtd_pedido_planejados = qtd_pedido_planejados["PEDIDO"].unique().shape[0]



qtd_pedido_cancelado = (df_filtrado["STATUS"] == "CANCELADO").sum()


total_aguardando= df_filtrado.query('STATUS == "AGUARDANDO PAGAMENTO"')
total_aguardando_pagamento = total_aguardando["TOTAL"].sum()

# --------------------------------------------------------------------------------------

with card1:
    st.metric("QTD Pedidos",f"{qtd_pedidos:,.0f} 📄".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
with card2:
    st.metric("Concluídos",f"{qtd_pedido_concluido:,.0f} 🟢".replace(',', 'X').replace('.', ',').replace('X', '.'))   
    

with card3:
    st.metric("Pagamento Em Aberto",f'{qtd_aguardando_pagamento} 🔵')
    

with card4:
    st.metric("Planejados", f"{qtd_pedido_planejados} 🟣".replace(',', 'X').replace('.', ',').replace('X', '.'))
    

with card5:
    st.metric("Cancelados", f"{qtd_pedido_cancelado} 🔴".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
df_filtrado = df_filtrado.drop(columns=["data", "Ano","Mês","PARENT","SKU_CLIENTE"])
df_filtrado = df_filtrado["PEDIDO","EMISSAO","CLIENTE","DESCRICAO","QTD","VR_UNIT","TOTAL","STATUS"]

st.dataframe(df_filtrado,hide_index=True,use_container_width=True)

if st.button("Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()