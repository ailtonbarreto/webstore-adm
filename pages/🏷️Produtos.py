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
def insert_data(parent, sku, descricao_parent, descricao, categoria, vr_unit):
    try:
        conn = psycopg2.connect(
            host='gluttonously-bountiful-sloth.data-1.use1.tembo.io',
            database='postgres',
            user='postgres',
            password='MeSaIkkB57YSOgLO',
            port='5432'
        )

        # Usando placeholders para inserir os dados de forma segura
        insert_query = """
        INSERT INTO tembo.tb_venda ("PARENT", "SKU_CLIENTE", "DESCRICAO_PARENT", "DESCRICAO", "CATEGORIA", "VR_UNIT")
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        cursor = conn.cursor()
        cursor.execute(insert_query, (parent, sku, descricao_parent, descricao, categoria, vr_unit))
        conn.commit()

        st.write("Dados inseridos com sucesso!")
    except Exception as e:
        st.write(f"Erro ao inserir dados: {e}")
    finally:
        if conn:
            conn.close()

            
if st.button("💾"):
    insert_data()