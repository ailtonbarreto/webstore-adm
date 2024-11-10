import streamlit as st
import psycopg2

st.set_page_config(page_title="Painel de Adm - Webstore", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.image("header.png", width=1300)

# Entrada dos dados
parent = st.number_input("Parent", format="%.0f", step=1)  # Use 0 casas decimais e um incremento de 1
parent = int(parent)  # Garantir que o valor é um inteiro

sku = st.text_input("SKU")

descricao_parent = st.text_input("Descrição Parent")
descricao = st.text_input("Descrição")
categoria = st.text_input("Categoria")

vr_unit = st.number_input("Valor Unit", format="%.2f")
vr_unit = float(vr_unit)  # Garantir que o valor é float

# Função de inserção
def insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent):
    try:
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
        INSERT INTO tembo.tb_produto ("PARENT", "SKU", "DESCRICAO", "CATEGORIA", "VR_UNIT", "DESCRICAO_PARENT")
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

# Botão para inserir os dados
if st.button("💾 Inserir Dados"):
    # Verifica se todos os campos foram preenchidos
    if sku and descricao and categoria and vr_unit > 0:  # Verificação para garantir que os campos necessários sejam preenchidos
        insert_data(parent, sku, descricao, categoria, vr_unit, descricao_parent)
    else:
        st.write("Por favor, preencha todos os campos necessários.")

# Exibindo os dados inseridos para confirmação
st.write("Dados inseridos:", parent, sku, descricao, categoria, vr_unit, descricao_parent)
