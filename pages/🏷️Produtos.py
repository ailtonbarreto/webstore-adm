import streamlit as st
import psycopg2

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.image("header.png", width=1300)


tab1, tab2 = st.tabs(["Visão Geral", "Cadastrar Produto"])

with tab1:
    st.write("🚧Em construção")


# ------------------------------------------------------------------------------------------------------------------
with tab2:
    parent = st.number_input("Parent", step=1)
    parent = int(parent)

    sku = st.text_input("SKU")

    descricao_parent = st.text_input("Descrição Parent")
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")

    vr_unit = st.number_input("Valor Unit", format="%.2f")
    vr_unit = float(vr_unit)

    # Função de inserção
    def insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent):
        try:
 
            conn = psycopg2.connect(
                host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
                database='postgres',
                user='postgres',
                password='MeSaIkkB57YSOgLO',
                port='5432'
            )


            insert_query = """
            INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "DESCRICAO_PARENT")
            VALUES (%s, %s, %s, %s, %s, %s);
            """

  
            cursor = conn.cursor()
            cursor.execute(insert_query, (parent, sku, descricao, categoria, vr_unit, descricao_parent))
            conn.commit()

            st.write("Dados inseridos com sucesso!")
        except Exception as e:
            st.write(f"Erro ao inserir dados: {e}")
        finally:
            if conn:
                conn.close()

 
    if st.button("💾"):
 
        if sku and descricao and categoria and vr_unit > 0:
            insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent)
        else:
            st.write("Por favor, preencha todos os campos necessários.")

