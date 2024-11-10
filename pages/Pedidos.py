import streamlit as st
import pandas as pd
import psycopg2
import plotly_express as px
import datetime


st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

st.image("header.png",width=1300)


cardpd1, cardpd2, cardpd3, cardpd4, cardpd5, cardpd6, cardpd7, = st.columns([2,2,2,2,2,1.5,1.5])
col1a, = st.columns(1)
st.divider()


# -------------------------------------------------------------------------------------------------------
# SELECT CARREGAR DATAFRAME

consulta = """
SELECT 
    v."PEDIDO",
    v."SKU_CLIENTE",
    v."EMISSAO",
    v."PARENT",
    p."DESCRICAO_PARENT",
    p."CATEGORIA",
    v."QTD",
    v."VR_UNIT",
    v."STATUS",
    c."CLIENTE"
FROM 
    tembo.tb_venda AS v
LEFT JOIN (
    SELECT DISTINCT ON ("PARENT") "PARENT", "DESCRICAO_PARENT", "CATEGORIA"
    FROM tembo.tb_produto
    ORDER BY "PARENT"
) AS p ON v."PARENT" = p."PARENT"
LEFT JOIN tembo.tb_cliente AS c ON v."SKU_CLIENTE" = c."SKU_CLIENTE";
"""

# -------------------------------------------------------------------------------------------------------

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
df['EMISSAO'] = pd.to_datetime(df['EMISSAO'])
df["Ano"] = df["EMISSAO"].dt.year
df["Mês"] = df["EMISSAO"].dt.month
df["Dia"] = df["EMISSAO"].dt.day


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


today = datetime.datetime.now().date()
inicio = today - datetime.timedelta(days=120)

# ----------------------------------------------------------------------------------
# filtros pedido


    
with cardpd6:
    filtro_inicio2 = st.date_input("Data Início",inicio,format= "DD/MM/YYYY")
        
with cardpd7:
    filtro_fim2 = st.date_input("Data Fim","today",format= "DD/MM/YYYY")


df_filtrado_ped = df.query('@filtro_inicio2 <= `EMISSAO` <= @filtro_fim2')


df_filtrado_ped["TOTAL"] = df_filtrado_ped["QTD"] * df_filtrado_ped["VR_UNIT"]

qtd_pedidos2 = df_filtrado_ped["PEDIDO"].nunique()

qtd_pg_aberto = df_filtrado_ped.query('STATUS == "AGUARDANDO PAGAMENTO"')
qtd_pg_aberto = qtd_pg_aberto["PEDIDO"].nunique()


qtd_pedido_concluido = df_filtrado_ped.query('STATUS == "CONCLUIDO"')
qtd_pedido_concluido = qtd_pedido_concluido["PEDIDO"].nunique()

qtd_pedido_planejados = df_filtrado_ped.query('STATUS == "PLANEJADO"')
qtd_pedido_planejados = qtd_pedido_planejados["PEDIDO"].nunique()


qtd_pedido_aguardando_conf = df_filtrado_ped.query('STATUS == "AGUARDANDO CONFIRMACAO"')
qtd_pedido_aguardando_conf = qtd_pedido_aguardando_conf["PEDIDO"].nunique()


total_aguardando= df_filtrado_ped.query('STATUS == "AGUARDANDO PAGAMENTO"')
total_aguardando_pagamento = total_aguardando["TOTAL"].sum()


# ---------------------------------------------------------------------------------------

with cardpd1:
    st.metric("QTD Pedidos",f"📄{qtd_pedidos2:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))   
with cardpd2:
    st.metric("Concluídos",f"🟢{qtd_pedido_concluido:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
with cardpd3:
    st.metric("Aguardando Confirmação",f"🟡{qtd_pedido_aguardando_conf:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))   
with cardpd4:
    st.metric("Pagamento Em Aberto",f"🔵{qtd_pg_aberto:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))  
with cardpd5:
    st.metric("Planejados",f"🟣{qtd_pedido_planejados:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))  