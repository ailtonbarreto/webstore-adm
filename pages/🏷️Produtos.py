import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.image("header.png", width=300)


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
      
        query = "SELECT * FROM tembo.tb_produto;"
        
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    

    if conn:
        conn.close()
    return df

df = load_produtos()

# -------------------------------------------------------------------------------------------------------



with tab1:
    col1, = st.columns(1)
    col2, = st.columns(1)
    

    with col1:

        produto_filtro = st.text_input("Pesquisar pelo SKU ou Nome do Produto", "")
        with col2:
            if produto_filtro:
        
                df_produto = df[
                    df['SKU'].astype(str).str.contains(produto_filtro, case=False) |
                    df['DESCRICAO'].str.contains(produto_filtro, case=False)
                ]

                if not df_produto.empty:
                    st.subheader(f"**Foram encontrados {len(df_produto)} produto(s):**",anchor=False)
                    for index, row in df_produto.iterrows():
                        st.subheader(row['DESCRICAO'], anchor=False)
                        st.image(row['IMAGEM'], width=200)
                        st.text(f"SKU: {row['SKU']}")
                        st.markdown("---")
                else:
                    st.write("Nenhum produto encontrado.")




    if st.button("🔁 Atualizar"):
        st.cache_data.clear()
        st.rerun()


# ------------------------------------------------------------------------------------------------------------------
# CADASTRAR PRODUTO

with tab2:
    parent = st.number_input("Parent", step=1)
    parent = int(parent)

    # O SKU será gerado automaticamente
    descricao_parent = st.text_input("Descrição Parent")
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")
    url = st.text_input("URL da Imagem")
    vr_unit = st.number_input("Valor Unit", format="%.2f")
    vr_unit = float(vr_unit)

    # Função de inserção
    def insert_data(parent, descricao, categoria, vr_unit, descricao_parent, url):
        try:
            conn = psycopg2.connect(
                host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                database='postgres',
                user='postgres',
                password='MeSaIkkB57YSOgLO',
                port='5432'
            )

            # Consulta para pegar o maior SKU atual
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(\"SKU\") FROM tembo.tb_produto")
            max_sku = cursor.fetchone()[0]

            # Se não houver SKU registrado, o primeiro SKU será 1
            if max_sku is None:
                sku = 1
            else:
                sku = max_sku + 1

            # Inserção de dados com o SKU gerado automaticamente
            insert_query = """
            INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "DESCRICAO_PARENT", "IMAGEM")
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

            # Garantir que o sku seja um número inteiro
            cursor.execute(insert_query, (parent, int(sku), descricao, categoria, vr_unit, descricao_parent, url))
            conn.commit()

            st.write("Dados inseridos com sucesso!")
        except Exception as e:
            st.write(f"Erro ao inserir dados: {e}")
        finally:
            if conn:
                conn.close()

    if st.button("💾 Salvar"):
        if descricao and categoria and vr_unit > 0:
            insert_data(parent, descricao, categoria, vr_unit, descricao_parent, url)
        else:
            st.write("Por favor, preencha todos os campos necessários.")


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

