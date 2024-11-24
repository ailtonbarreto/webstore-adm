import streamlit as st
import psycopg2
import pandas as pd

#
st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")


with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


tab1, tab2 = st.tabs(["Pesquisar Produto", "Cadastrar Produto"])


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
                SELECT 
                    cp."PARENT",
                    p."SKU",
                    p."DESCRICAO",
                    cp."IMAGEM",
                    cp."CATEGORIA",
                    cp."VR_UNIT",
                    cp."DESCRICAO_PARENT"
                FROM 
                    tembo.tb_produto AS p
                JOIN 
                    tembo.tb_produto_parent AS cp
                ON 
                    p."PARENT" = cp."PARENT";
                """
        
        
        
        df = pd.read_sql_query(query, conn)
        
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    finally:
        if conn:
            conn.close()
    return df

df = load_produtos()

# ------------------------------------------------------------------------------------------------------------------
# PESQUISAR PRODUTO

with tab1:
    col1, = st.columns(1)
    col2, col3 = st.columns([2,1])
    
    
    with col1:
        produto_filtro = st.text_input("Pesquise SKU", placeholder="Digite e tecle Enter")
        produto_filtro = produto_filtro.upper()
        
    with col2:
        st.subheader("Resultado da Pesquisa",anchor=False)
        
        if produto_filtro:
            df_produto = df.query('SKU == @produto_filtro')
            if not df_produto.empty:
                for index, row in df_produto.iterrows():
                    st.image(row['IMAGEM'], width=500)
                    st.subheader(row['DESCRICAO'],anchor=False)
                with col3:
                    st.subheader("Informações",anchor=False)
                    st.write(f"SKU: {row['SKU']}")
            else:
                st.write("Nenhum produto encontrado.")
    

# ------------------------------------------------------------------------------------------------------------------
# CADASTRAR PRODUTO

with tab2:
    
    col1, = st.columns(1)
    
    with col1:

            tipo = st.selectbox("Tipo", ["Produto Pai", "Produto Variação"])

            if tipo == "Produto Pai":
                descricao_parent = st.text_input("Descrição")
                categoria = st.selectbox("Categoria", ["Chapéu", "Roupas", "Mochila", "Tênis"])
                vr_unit = st.number_input("Valor Unit", format="%.2f")
                url = st.text_input("URL da Imagem")
            else:
                produto_pai = st.selectbox("Produto Pai", df["DESCRICAO_PARENT"].unique())
                df_parent = df.query('DESCRICAO_PARENT == @produto_pai')
                parent = df_parent["PARENT"].values[0]
                categoria = df_parent["CATEGORIA"].values[0]
                vr_unit = df_parent["VR_UNIT"].values[0]
                url = df_parent["IMAGEM"].values[0]
                variacao = st.selectbox("Variação", ["UN", "P", "M", "G", "GG", "EG", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"])
                sku = f"{parent}-{variacao}"
                descricao = f"{produto_pai}-{variacao}"
                
               
# ---------------------------------------------------------------------------------------------------
# FUNCAO CADASTRAR PRODUTO PAI

    def insert_parent(descricao_parent, categoria, vr_unit, url):
   
        conn = psycopg2.connect(host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',database='postgres',user='postgres',password='MeSaIkkB57YSOgLO',port='5432')

        cursor = conn.cursor()

        cursor.execute("SELECT MAX(\"PARENT\") FROM tembo.tb_produto_parent")
        max_parent = cursor.fetchone()[0]

        parent = max_parent + 1 if max_parent else 1

        insert_query = """
                INSERT INTO tembo.tb_produto_parent ("PARENT", "DESCRICAO_PARENT", "CATEGORIA", "VR_UNIT", "IMAGEM")
                VALUES (%s, %s, %s, %s, %s);
                """

        cursor.execute(insert_query, (parent, descricao_parent, categoria, vr_unit, url))
        conn.commit()

        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------------------------------------------------------
# FUNCAO CADASTRAR VARIACAO

    def insert_variacao(parent, sku, descricao, categoria, vr_unit):
            
        conn = psycopg2.connect(
                    host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                    database='postgres',
                    user='postgres',
                    password='MeSaIkkB57YSOgLO',
                    port='5432'
                )

        cursor1 = conn.cursor()

        parent = int(parent)
        sku = str(sku)
        descricao = str(descricao)
        vr_unit = float(vr_unit)


        insert_query1 = """
        INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT")
        VALUES (%s, %s, %s, %s, %s);
        """

        cursor1.execute(insert_query1, (parent, sku, descricao, categoria, vr_unit))
        conn.commit()

   
        if cursor1:
         cursor1.close()
        if conn:
         conn.close()
    with col1:
        if tipo == "Produto Pai":
                if st.button("Cadastrar Produto 💾"):
                    if descricao_parent and categoria and vr_unit > 0 and url:
                        insert_parent(descricao_parent, categoria, vr_unit, url)
                        st.success("Produto inserido com sucesso!")
                    else:
                        st.warning("Por favor, preencha todos os campos necessários.")
        else:
                if st.button("Cadastrar Variação 💾"):
                    if sku and descricao and categoria and vr_unit > 0:
                        insert_variacao(parent, sku, descricao, categoria, vr_unit)
                        st.success("Produto inserido com sucesso!")

                    else:
                        st.warning("Por favor, preencha todos os campos necessários.")

if st.button("🔁 Atualizar"):
    st.cache_data.clear()
    st.rerun()
# ---------------------------------------------------------------------------------------------------------
# ESTILIZACAO

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

