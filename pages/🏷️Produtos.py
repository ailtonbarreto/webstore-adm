import streamlit as st
import pandas as pd
import psycopg2
import datetime


st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

st.image("header.png",width=1300)

parent = st.number_input("Parent")

sku = st.text_input("SKU")

descricao_parent = st.text_input("Descrição Parent")

descricao = st.text_input("Descrição")

categoria = st.text_input("Categoria")

vr_unit = st.number_input("Valor Unit")

# Função para inserir dados (exemplo de INSERT)
import psycopg2
import streamlit as st

# Função de inserção
def insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent):
    try:
        # Verificando e mostrando os parâmetros antes de usar
        st.write(f"Parâmetros recebidos: parent={parent}, sku={sku}, descricao={descricao}, categoria={categoria}, vr_unit={vr_unit}, descricao_parent={descricao_parent}")
        
        # Garantir que os tipos estão corretos
        sku = st(sku)  # Garantir que SKU seja inteiro
        vr_unit = float(vr_unit)  # Garantir que VR_UNIT seja float
        parent = int(parent)

        # Conexão com o banco de dados
        conn = psycopg2.connect(
            host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
            database='postgres',
            user='postgres',
            password='MeSaIkkB57YSOgLO',
            port='5432'
        )

        # Consulta SQL de INSERT com placeholders
        insert_query = """
        INSERT INTO tembo.tb_venda ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "DESCRICAO_PARENT")
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        # Executando a query com os dados capturados
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
    insert_data()