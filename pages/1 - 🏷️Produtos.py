import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


tab1, tab2 = st.tabs(["Pesquisar Produto", "Cadastrar Produto"])


# -------------------------------------------------------------------------------------------------------

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
                p."SKU",
                p."DESCRICAO",
                cp."IMAGEM",
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
    

    if conn:
        conn.close()
    return df

df = load_produtos()

# -------------------------------------------------------------------------------------------------------
# PESQUISAR PRODUTO

with tab1:
    col1, = st.columns(1)
    col2, = st.columns(1)
    col3, = st.columns(1)
    

    with col2:
        st.subheader("Resultado da Pesquisa",anchor=False)
            
    with col1:
        produto_filtro = st.text_input("Pesquise SKU", placeholder="Digite e tecle Enter")
        produto_filtro = produto_filtro.upper()
        
        with col2:
            if produto_filtro:
                
                df_produto = df.query('SKU == @produto_filtro')

                if not df_produto.empty:
                    with col2:
                        for index, row in df_produto.iterrows():
                            st.image(row['IMAGEM'], width=500)
                            st.subheader(row['DESCRICAO'], anchor=False)
                            st.write(f"SKU: {row['SKU']}")
                else:
                    st.write("Nenhum produto encontrado.")

    with col3:
        st.subheader("Infomações",anchor=False)
       

if st.button("🔁 Atualizar"):
    st.cache_data.clear()
    st.rerun()


# ------------------------------------------------------------------------------------------------------------------
# CADASTRAR PRODUTO

with tab2:
    col1, = st.columns(1)

    with col1:
        tipo = st.selectbox("Tipo",["Produto Pai","Produto Variação"])

        if tipo == "Produto Pai":
            descricao_parent = st.text_input("Descrição")
            categoria = st.selectbox("Categoria", ["Chapéu", "Roupas", "Mochila", "Tênis"])
            vr_unit = st.number_input("Valor Unit", format="%.2f")
            url = st.text_input("URL da Imagem")
        else:
            produto_pai = st.selectbox("Produto Pai",df["DESCRICAO_PARENT"].unique())
            variacao = st.selectbox("Variação",["UN","P","M","G","GG","EG","34","35","36","37","38","39","40","41","42","43","44"])





# ----------------------------------------------------------------------------------------------
#INSERIR PRODUTO PAI

        def insert_parent(descricao_parent, categoria, vr_unit, url):
            try:
                conn = psycopg2.connect(
                    host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                    database='postgres',
                    user='postgres',
                    password='MeSaIkkB57YSOgLO',
                    port='5432'
                )

                cursor = conn.cursor()

                # Obtém o maior valor de "PARENT"
                cursor.execute("SELECT MAX(\"PARENT\") FROM tembo.tb_produto_parent")
                max_parent = cursor.fetchone()[0]

                parent = max_parent + 1 if max_parent else 1

                # Query de inserção
                insert_query = """
                INSERT INTO tembo.tb_produto_parent ("PARENT", "DESCRICAO_PARENT", "CATEGORIA", "VR_UNIT", "IMAGEM")
                VALUES (%s, %s, %s, %s, %s);
                """

                cursor.execute(insert_query, (parent, descricao_parent, categoria, vr_unit, url))
                conn.commit()

                st.success("Dados inseridos com sucesso!")
            except Exception as e:
                st.error(f"Erro ao inserir dados: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

# ------------------------------------------------------------------------------------------------------









        # Botão de salvar
        if st.button("Salvar 💾"):
            if descricao_parent and categoria and vr_unit > 0 and url:
                insert_parent(descricao_parent, categoria, vr_unit, url)
                st.rerun()
            else:
                st.warning("Por favor, preencha todos os campos necessários.")


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

