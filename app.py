import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
    
    
tab1, tab2 = st.tabs(["Dashboard","Pedidos"])

with tab1:
    card1, card2, card3, card4, card5, card6, card7,card8 = st.columns([2,2,2,2,2,2,1,1])



# -------------------------------------------------------------------------------------------------------
# DATABASE POSTGRES NA NUVEM

consulta = """
SELECT 
    v."PEDIDO",
    v."SKU_CLIENTE",
    v."EMISSAO",
    v."PARENT",
    p."DESCRICAO_PARENT",
    v."QTD",
    v."VR_UNIT",
    v."STATUS"
FROM 
    tembo.tb_venda AS v
LEFT JOIN (
    SELECT DISTINCT ON ("PARENT") "PARENT", "DESCRICAO_PARENT"
    FROM tembo.tb_produto
    ORDER BY "PARENT"
) AS p ON v."PARENT" = p."PARENT";
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
with tab1:
    
    with card7:
        filtro_inicio = st.date_input("Início",pd.to_datetime("2024-01-01").date(),format= "DD/MM/YYYY")
        
    with card8:
        filtro_fim = st.date_input("Fim","today",format= "DD/MM/YYYY")

    df_filtrado = df.query('@filtro_inicio <= `EMISSAO` <= @filtro_fim')

    df_filtrado["TOTAL"] = df_filtrado["QTD"] * df_filtrado["VR_UNIT"]



# ----------------------------------------------------------------------------------
# kpis

qtd_pedidos = df_filtrado["PEDIDO"].nunique()

total = df_filtrado["TOTAL"].sum()

ticket_medio = total / qtd_pedidos

qtd_pg_aberto = df_filtrado.query('STATUS == "AGUARDANDO PAGAMENTO"')
qtd_pg_aberto = qtd_pg_aberto["PEDIDO"].nunique()


qtd_pedido_concluido = df_filtrado.query('STATUS == "CONCLUIDO"')
qtd_pedido_concluido = qtd_pedido_concluido["PEDIDO"].nunique()

qtd_pedido_planejados = df_filtrado.query('STATUS == "PLANEJADO"')
qtd_pedido_planejados = qtd_pedido_planejados["PEDIDO"].nunique()


qtd_pedido_aguardando_conf = df_filtrado.query('STATUS == "AGUARDANDO CONFIRMACAO"')
qtd_pedido_aguardando_conf = qtd_pedido_aguardando_conf["PEDIDO"].nunique()


qtd_pedido_cancelado = df_filtrado.query('STATUS == "CANCELADO"')
qtd_pedido_cancelado = qtd_pedido_cancelado["PEDIDO"].nunique()


total_aguardando= df_filtrado.query('STATUS == "AGUARDANDO PAGAMENTO"')
total_aguardando_pagamento = total_aguardando["TOTAL"].sum()

# --------------------------------------------------------------------------------------
with tab1:
    with card1:
        st.metric("QTD Pedidos",f"{qtd_pedidos:,.0f} 📄".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
    with card2:
        st.metric("Aguardando Confirmação", f"{qtd_pedido_aguardando_conf} 🟡".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
    with card3:
        st.metric("Concluídos",f"{qtd_pedido_concluido:,.0f} 🟢".replace(',', 'X').replace('.', ',').replace('X', '.'))   
        

    with card4:
        st.metric("Pagamento Em Aberto",f'{qtd_pg_aberto} 🔵')
        

    with card5:
        st.metric("Planejados", f"{qtd_pedido_planejados} 🟣".replace(',', 'X').replace('.', ',').replace('X', '.'))
        

    with card6:
        st.metric("Cancelados", f"{qtd_pedido_cancelado} 🔴".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    st.dataframe(df_filtrado,hide_index=True,use_container_width=True)
    
with tab2:
    pedido = st.text_input("PEDIDO")
    df_pedido = df_filtrado.query('PEDIDO == @pedido')
    st.dataframe(df_pedido,use_container_width=True)
    
# df_filtrado = df_filtrado.drop(columns=["data", "Ano","Mês","PARENT","SKU_CLIENTE"])
# df_filtrado = df_filtrado[["PEDIDO","EMISSAO","SKU_CLIENTE","DESCRICAO_PARENT","QTD","VR_UNIT","TOTAL","STATUS"]]




if st.button("Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()