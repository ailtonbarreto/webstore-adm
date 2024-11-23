import streamlit as st
import pandas as pd
import psycopg2


st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)


tab1, tab2,tab3 = st.tabs(["Pedidos", "Alterar Status","Inserir Pedido"])


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

# -------------------------------------------------------------------------------------------------------
# INSERIR PEDIDO

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        lista = [""] + df["CLIENTE"].unique().tolist()
        cliente = st.selectbox("Cliente",lista)



insert = """
    INSERT INTO tembo.tb_venda ("PEDIDO", "EMISSAO", "ENTREGA", 
    "SKU_CLIENTE", "SKU", "PARENT", "QTD", "VR_UNIT", "SEQUENCIA", "STATUS")
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING *;
    """

# ----------------------------------------------------------------------------------
# PEDIDOS

with tab1:
    
    cardpd1, cardpd2, cardpd3, cardpd4, cardpd5, cardpd6, cardpd7 = st.columns([2,2,2,2,2,1.5,1.5])
    col1, = st.columns(1)
    col2, = st.columns(1)
    
    with cardpd6:
        filtro_inicio2 = st.date_input("Data Início","today",format= "DD/MM/YYYY")
            
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

    total_cancelado= df_filtrado_ped.query('STATUS == "CANCELADO"')
    total_cancelado = total_cancelado["PEDIDO"].nunique()
    
    total_total = df_filtrado_ped["TOTAL"].sum()

    # ---------------------------------------------------------------------------------------

    with cardpd1:
        st.metric("Concluídos",f"🟢{qtd_pedido_concluido:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    with cardpd2:
        st.metric("Aguardando Confirmação",f"🟡{qtd_pedido_aguardando_conf:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))   
    with cardpd3:
        st.metric("Pagamento Em Aberto",f"🔵{qtd_pg_aberto:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))    
    with cardpd4:
        st.metric("Planejados",f"🟣{qtd_pedido_planejados:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    with cardpd5:
        st.metric("Cancelados",f"🔴{total_cancelado:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')) 

    with col1:
        if df_filtrado_ped.empty:
            st.error("Nenhum dado disponível.")
        else:
            st.subheader("Pedidos No Período",anchor=False)
            df_filtrado_ped = df_filtrado_ped[["EMISSAO","PEDIDO","CLIENTE","DESCRICAO_PARENT","QTD","VR_UNIT","TOTAL","STATUS"]]
            df_filtrado_ped["EMISSAO"] = df_filtrado_ped["EMISSAO"].dt.strftime('%d/%m/%Y')
            st.dataframe(df_filtrado_ped, use_container_width=True, hide_index=True)
    with col2:
        st.write("Total", total_total)     
    
# ---------------------------------------------------------------------------------------
# ALTERAR STATUS DOS PEDIDOS

           
with tab2:
    col1, col2 = st.columns(2)
    col3, = st.columns(1)
    with col1:
        filtro_pedido = st.text_input("Pedido")
    with col2:
        novo_status = st.selectbox(
            "Status",
            ["AGUARDANDO CONFIRMACAO", "AGUARDANDO PAGAMENTO","PLANEJADO" ,"CONCLUIDO"]
        )
    with col3:
        def update_pedido(filtro_pedido, novo_status):
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
                cursor = conn.cursor()

                # Atualiza o pedido com o novo status
                query = f"""
                UPDATE tembo.tb_venda
                SET "STATUS" = '{novo_status}'
                WHERE "PEDIDO" = '{filtro_pedido}';
                """
                cursor.execute(query)
                conn.commit()
                st.success("Pedido atualizado com sucesso!")

                # Consulta atualizada
                consulta_query = f"""
                SELECT * FROM tembo.tb_venda WHERE "PEDIDO" = '{filtro_pedido}';
                """
                df = pd.read_sql_query(consulta_query, conn)
                return df

            except Exception as e:
                st.error(f"Erro ao conectar: {e}")
            finally:
                if conn:
                    cursor.close()
                    conn.close()
        df_pedido = df.query('PEDIDO == @filtro_pedido')
        st.subheader("Resultado Da Pesquisa", anchor=False)
        df_pedido = df_pedido.drop(columns=["SKU_CLIENTE","Ano","Mês","Dia"])
        df_pedido = df_pedido[["EMISSAO","PEDIDO","CLIENTE","DESCRICAO_PARENT","QTD","VR_UNIT","STATUS"]]
        df_pedido["EMISSAO"] = df_pedido["EMISSAO"].dt.strftime('%d/%m/%Y')
        st.dataframe(df_pedido,use_container_width=True,hide_index=True)
        if st.button("💾 Salvar"):
            if filtro_pedido:
                df_pedido_filtrado = update_pedido(filtro_pedido, novo_status)
            else:
                st.warning("Por favor, insira um número de pedido válido.")


# --------------------------------------------------------------------------------------

if st.button("🔁 Atualizar"):
    st.cache_data.clear()
    st.rerun()
    

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



style3 = """
    <style>
    [data-testid="stBaseButton-elementToolbar"]
    {
    display: none;
    }
    </style>
"""
st.markdown(style3, unsafe_allow_html=True)



style4 = """
    <style>
    [data-testid="stMetricValue"]
    {
    margin-top: 0.4vw;
    }
    </style>
"""
st.markdown(style4, unsafe_allow_html=True)