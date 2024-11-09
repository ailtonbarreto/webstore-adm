import streamlit as st
import pandas as pd
import psycopg2
import plotly_express as px
import datetime

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

st.image("header.png",width=1300)
    
tab1, tab2 = st.tabs(["Dashboard","Pedidos"])

with tab1:
    card1, card2, card3, card4, card5, card6, card7, = st.columns([2,2,2,2,2,1.5,1.5])
    col1, col2 = st.columns(2)
    col3, col4= st.columns(2)
    
with tab2:
    cardpd1, cardpd2, cardpd3, cardpd4, cardpd5, cardpd6, cardpd7, = st.columns([2,2,2,2,2,1.5,1.5])

    
# -------------------------------------------------------------------------------------------------------
# DATABASE POSTGRES NA NUVEM

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

# ----------------------------------------------------------------------------------

today = datetime.datetime.now().date()
inicio = today - datetime.timedelta(days=120)


# ----------------------------------------------------------------------------------
# filtros dash

with tab1:
    
    with card6:
        filtro_inicio = st.date_input("Início",inicio,format= "DD/MM/YYYY")
        
    with card7:
        filtro_fim = st.date_input("Fim","today",format= "DD/MM/YYYY")
        

df_filtrado = df.query('@filtro_inicio <= `EMISSAO` <= @filtro_fim')

df_filtrado["TOTAL"] = df_filtrado["QTD"] * df_filtrado["VR_UNIT"]

# ----------------------------------------------------------------------------------
# filtros pedido

with tab2:
    
    with cardpd6:
        filtro_inicio2 = st.date_input("Data Início",inicio,format= "DD/MM/YYYY")
        
    with cardpd7:
        filtro_fim2 = st.date_input("Data Fim","today",format= "DD/MM/YYYY")


df_filtrado_ped = df.query('@filtro_inicio2 <= `EMISSAO` <= @filtro_fim2')


df_filtrado_ped["TOTAL"] = df_filtrado_ped["QTD"] * df_filtrado_ped["VR_UNIT"]

qtd_pedidos2 = df_filtrado_ped["PEDIDO"].nunique()

# ----------------------------------------------------------------------------------
# kpis


qtd_pedidos = df_filtrado["PEDIDO"].nunique()

total = df_filtrado["TOTAL"].sum()

ticket_medio = total / qtd_pedidos


qtd_clientes = df_filtrado["CLIENTE"].nunique()
qtd_pedido_cancelado = df_filtrado.query('STATUS == "CANCELADO"')
qtd_pedido_cancelado = qtd_pedido_cancelado["PEDIDO"].nunique()

tx_cancelamento = qtd_pedido_cancelado / qtd_pedidos * 100

# -----------------------------------------------------------------------------------

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


# --------------------------------------------------------------------------------------
with tab1:
    with card1:
        st.metric("Valor Vendido",f"💰{total:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
    with card2:
        
        st.metric("QTD Pedidos",f"📄{qtd_pedidos:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))   
        
    with card3:
        st.metric("Ticket Médio", f"📈{ticket_medio:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))   
    
    with card4:
        st.metric("QTD Clientes",f'👔{qtd_clientes:,.0f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))

    with card5:
        st.metric("Tx Cancelamentos", f"🔴{tx_cancelamento:.2f}%")
        
# ---------------------------------------------------------------------------------------

with tab2:
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
# ---------------------------------------------------------------------------------------
with tab2:
    if df_filtrado_ped.empty:
        st.error("Nenhum dado disponível.")
    else:
        df_filtrado_ped = df_filtrado_ped[["EMISSAO","PEDIDO","CLIENTE","DESCRICAO_PARENT","QTD","VR_UNIT","TOTAL","STATUS"]]
        df_filtrado_ped["EMISSAO"] = df_filtrado_ped["EMISSAO"].dt.strftime('%d/%m/%Y')
        st.dataframe(df_filtrado_ped, use_container_width=True, hide_index=True)

    
# --------------------------------------------------------------------------------------
# graficos
barras_cores = "0F8F8F"

df_linha = df_filtrado.groupby("Dia")["TOTAL"].sum().reset_index()


graficocolunas = px.bar(df_linha,x="Dia",y="TOTAL",color_discrete_sequence=["#0F8F8F"])
graficocolunas.update_yaxes(showgrid=False)
graficocolunas.update_traces(showlegend=False)
graficocolunas.update_yaxes(showgrid=False,visible=True,title="")
graficocolunas.layout.xaxis.fixedrange = True
graficocolunas.layout.yaxis.fixedrange = True

# --------------------------------------------------------------------------------------

df_categoria = df_filtrado.groupby("CATEGORIA")["TOTAL"].sum().reset_index()
df_categoria = df_categoria.sort_values(by="TOTAL",ascending=True)

grafico_barras = px.bar(df_categoria, x="TOTAL",y="CATEGORIA",orientation="h",color_discrete_sequence=["#0F8F8F"],
                        text=df_categoria["TOTAL"].apply(lambda x: f'R$ {x:,.2f}'))
grafico_barras.update_yaxes(showgrid=False)
grafico_barras.update_traces(showlegend=False,textfont=dict(size=15,color='#ffffff'),textposition="auto")
grafico_barras.update_yaxes(showgrid=False,visible=True,title="")
grafico_barras.layout.xaxis.fixedrange = True
grafico_barras.layout.yaxis.fixedrange = True

# ---------------------------------------------------------------------------------------------------------
# tabela

df_tb = df_filtrado.groupby("CLIENTE")["TOTAL"].sum().reset_index()
df_tb = df_tb.sort_values(by="TOTAL",ascending=False)
df_tb["TOTAL"] = df_tb["TOTAL"].apply(lambda x: f'R$ {x:,.2f}')


# ---------------------------------------------------------------------------------------------------------
# ranking produtos
df_produto = df_filtrado.groupby("DESCRICAO_PARENT")["QTD"].count().reset_index()
df_produto = df_produto.sort_values(by="QTD",ascending=False)


# ---------------------------------------------------------------------------------------------------------

with tab1:
    with col4:
        st.subheader("Valor Vendido Por Categoria",anchor=False)
        st.plotly_chart(grafico_barras,use_container_width=True)



with tab1:
    with col1:
        st.subheader("Valor Vendido No Período",anchor=False)
        st.plotly_chart(graficocolunas,use_container_width=True)
        
    with col3:
        st.subheader("Ranking De Produtos",anchor=False)
        st.dataframe(df_produto,use_container_width=True,hide_index=True)
        
with tab1:
    with col2:
        st.subheader("Valor Vendido Por Clientes",anchor=False)
        st.dataframe(df_tb,use_container_width=True,hide_index=True)


if st.button("Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()
    
# ---------------------------------------------------------------------------------------------------------
# estilizacao

style1 = """
    <style>
    [data-testid="stColumn"]
    {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 5px 3px 5px rgba(0, 0, 0, 0.3);
    }
    </style>
"""
st.markdown(style1, unsafe_allow_html=True)


# 