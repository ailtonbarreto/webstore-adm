import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.subheader("Estoque",anchor=False)

tab1, tab2 = st.tabs(["Consultar Estoque", "Adicionar Movimentação"])


# -------------------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------------------
# CARREGAR PRODUTOS

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
        
        query = """

                WITH estoque_calculado AS (
                    SELECT 
                        e."SKU",
                        SUM(CASE 
                                WHEN e."TIPO" = 'E' THEN e."QTD"
                                WHEN e."TIPO" = 'S' THEN -e."QTD"
                                ELSE 0
                            END) AS "ESTOQUE_TOTAL"
                    FROM 
                        tembo.tb_mov_estoque AS e
                    GROUP BY 
                        e."SKU"
                )
                SELECT 
                    cp."PARENT",
                    p."SKU",
                    p."DESCRICAO",
                    cp."IMAGEM",
                    cp."CATEGORIA",
                    cp."VR_UNIT",
                    p."ATIVO",
                    cp."DESCRICAO_PARENT",
                    COALESCE(ec."ESTOQUE_TOTAL", 0) AS "ESTOQUE"
                FROM 
                    tembo.tb_produto AS p
                JOIN 
                    tembo.tb_produto_parent AS cp
                ON 
                    p."PARENT" = cp."PARENT"
                LEFT JOIN 
                    estoque_calculado AS ec
                ON 
                    p."SKU" = ec."SKU";

                    
                """
     
        df = pd.read_sql_query(query, conn)

        
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    finally:
        if conn:
            conn.close()
    return df

df_estoque = load_produtos()


# ------------------------------------------------------------------------------------------------------------------
# PESQUISAR PRODUTO

with tab1:
    col1, = st.columns(1)
    col2, col3 = st.columns([1,2.5])
        
    with col1:
        produto_filtro = st.text_input("Pesquise SKU", placeholder="Digite e tecle Enter")
        produto_filtro = produto_filtro.upper()
        
    with col2:
        st.subheader("Imagem",anchor=False)
        
        if produto_filtro:
            
            df_produto = df_estoque.query('SKU == @produto_filtro')
            
            if not df_produto.empty:
                
                for index, row in df_produto.iterrows():
                    with col2:
                        
                        st.image(row['IMAGEM'], width=400)
                        st.write(f"{row['DESCRICAO']}",anchor=False)
                        
                    
                    with col3:

                        st.subheader("SITUAÇÃO",anchor=False)
                        if row['ATIVO'] == 1:
                            st.write("Ativo",anchor=False)
                        else:
                            st.write("Inativo",anchor=False)
                        
                        st.divider()
                        
                        
                        st.subheader("ESTOQUE",anchor=False)
                        df_qtd = df.query('SKU == @produto_filtro')
                        df_qtd = df_qtd["QTD"].sum()
                        st.write("",f'{df_qtd:,.0f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
                        
                        st.divider()
           
                        st.subheader("SKU do Produto",anchor=False)
                        st.write(f"{row['SKU']}",ancor=False)
                        
                    
                        st.divider()
                        
                        st.subheader("Localização",anchor=False)
                        st.write("A.01.01.01")
            else:
                st.write("Nenhum produto encontrado.")
                
# -------------------------------------------------------------------------------------------------------
# ATUALIZAR VISUAL

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
