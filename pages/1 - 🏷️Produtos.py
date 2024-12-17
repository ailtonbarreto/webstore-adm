import streamlit as st
import psycopg2
import pandas as pd
from time import sleep

#
st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")


with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.subheader("Produtos",anchor=False)

tab2, tab3 = st.tabs(["Cadastrar Produto","Ativar/Inativar"])

# ------------------------------------------------------------------------------------------------------------------
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
                SELECT 
                    cp."PARENT",
                    p."SKU",
                    p."DESCRICAO",
                    cp."IMAGEM",
                    cp."CATEGORIA",
                    cp."VR_UNIT",
                    p."ATIVO",
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


# ------------------------------------------------------------------------------------------------------------------
# CARREGAR PRODUTOS PAI
 
@st.cache_data
def load_parent():
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
        
        queryparent = """
                SELECT 
                    cp."PARENT",
                    cp."IMAGEM",
                    cp."CATEGORIA",
                    cp."VR_UNIT",
                    cp."DESCRICAO_PARENT"
                FROM 
                    tembo.tb_produto_parent AS cp
                """
        
        df_parent = pd.read_sql_query(queryparent, conn)

        
    except Exception as e:
        st.write(f"Erro ao conectar: {e}")
    finally:
        if conn:
            conn.close()
    return df_parent


df_parent = load_parent()

df = load_produtos()


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
                produto_pai = st.selectbox("Produto Pai", df_parent["DESCRICAO_PARENT"].unique())
                df_parent = df_parent.query('DESCRICAO_PARENT == @produto_pai')
                parent = df_parent["PARENT"].values[0]
                categoria = df_parent["CATEGORIA"].values[0]
                vr_unit = df_parent["VR_UNIT"].values[0]
                variacao = st.selectbox("Variação", ["UN", "P", "M", "G", "GG", "EG", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"])
                sku = f"{parent}-{variacao}"
                descricao = f"{produto_pai}-{variacao}"
                ativo = 1
                
                st.write(f'Sku do Produto: {sku}')
      
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
# EDITAR STATUS DO PRODUTO CADASTRADO

def editar_produto(status_produtos, sku_produto):
    
    try:

        conn = psycopg2.connect(
            host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
            database='postgres',
            user='postgres',
            password='MeSaIkkB57YSOgLO',
            port='5432'
        )
        cursor = conn.cursor()

        update_query = """
            UPDATE tembo.tb_produto
            SET "ATIVO" = %s
            WHERE "SKU" = %s;
        """
        cursor.execute(update_query, (status_produtos, sku_produto))
        conn.commit()

        st.success("Produto atualizado com sucesso!")

    except psycopg2.Error as e:
        st.error(f"Ocorreu um erro ao editar o produto: {e}")

    finally:
      
        if cursor:
            cursor.close()
        if conn:
            conn.close()

with tab3:
 
    cola, colb = st.columns(2)
    colc, = st.columns(1)

    with cola:
        sku_produto = st.text_input("SKU do Produto")

    with colb:
        situacao = st.selectbox("Situação", ["Ativo", "Inativo"])


    status_produtos = 1 if situacao == "Ativo" else 0
    
    df_status = df.query('SKU == @sku_produto')
    df_status = df_status[["PARENT","DESCRICAO","CATEGORIA","ATIVO"]]
    

    with colc:
        if df_status.empty:
            st.error("Nenhum Produto Encontrado.")
        else:
            st.dataframe(df_status,use_container_width=True,hide_index=True)

    with colc:
        if st.button("💾 Salvar Edição"):
            if sku_produto:
                editar_produto(status_produtos, sku_produto)
                st.cache_data.clear()
            else:
                st.warning("Por favor, insira o SKU do produto.")

# ---------------------------------------------------------------------------------------------------
# FUNCAO CADASTRAR VARIACAO
    def insert_variacao(parent, sku, descricao, categoria, vr_unit):
        try:
            conn = psycopg2.connect(
                host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                database='postgres',
                user='postgres',
                password='MeSaIkkB57YSOgLO',
                port='5432'
            )

            cursor1 = conn.cursor()

            
            parent = int(parent)
            descricao = str(descricao)
            vr_unit = float(vr_unit)
            ativo = 0

            
            insert_query1 = """
            INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "ATIVO")
            VALUES (%s, %s, %s, %s, %s, %s);
            """

            cursor1.execute(insert_query1, (parent, sku, descricao, categoria, vr_unit, ativo))
            conn.commit()
        except Exception as e:
            st.error(f"Erro ao inserir variação: {e}")
        finally:
            if cursor1:
                cursor1.close()
            if conn:
                conn.close()

with tab2:
        
    with col1:
        if tipo == "Produto Pai":
            if st.button("Cadastrar Produto 💾"):
                if descricao_parent and categoria and vr_unit > 0 and url:
                    insert_parent(descricao_parent, categoria, vr_unit, url)
                    st.success("Produto inserido com sucesso!")
                    sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Por favor, preencha todos os campos necessários.")
        else:
            if st.button("Cadastrar Variação 💾"):
                if sku and descricao and categoria and vr_unit > 0:
                    insert_variacao(parent, sku, descricao, categoria, vr_unit)
                    st.success("Produto inserido com sucesso!")
                    sleep(1)
                    st.cache_data.clear()
                    st.rerun()
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

