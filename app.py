import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração inicial
st.set_page_config(page_title="Meu_Mercado", page_icon="🛒")

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('compras_db.sqlite', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            marca TEXT,
            mercado TEXT,
            preco REAL,
            data TEXT
        )
    ''')
    conn.commit()
    return conn

conn = conectar_banco()

st.title("🛒 Gestor de Compras e Preços")

# Menu de navegação
aba1, aba2 = st.tabs(["📝 Cadastrar Compra", "📊 Comparar Preços"])

with aba1:
    st.header("Adicionar Novo Item")
    with st.form("form_compra", clear_on_submit=True):
        nome = st.text_input("Nome do Produto (ex: Arroz 5kg)").strip().capitalize()
        marca = st.text_input("Marca").strip().capitalize()
        mercado = st.text_input("Mercado / Loja").strip().capitalize()
        preco = st.number_input("Preço Pago (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data da Compra", datetime.now())
        
        if st.form_submit_button("Salvar no Histórico"):
            if nome and mercado and preco > 0:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO compras (produto, marca, mercado, preco, data) VALUES (?, ?, ?, ?, ?)",
                             (nome, marca, mercado, preco, str(data)))
                conn.commit()
                st.success(f"Item '{nome}' salvo com sucesso!")
            else:
                st.error("Por favor, preencha Nome, Mercado e Preço.")

with aba2:
    st.header("🔍 Onde está mais barato?")
    df = pd.read_sql_query("SELECT * FROM compras", conn)
    
    if not df.empty:
        produtos_unicos = sorted(df['produto'].unique())
        escolha = st.selectbox("Selecione o produto para análise:", produtos_unicos)
        
        # Filtra os dados pelo produto escolhido
        dados_prod = df[df['produto'] == escolha].sort_values(by='preco')
        
        # Destaque para o melhor preço
        melhor_opcao = dados_prod.iloc[0]
        st.info(f"💡 O melhor preço para **{escolha}** foi **R$ {melhor_opcao['preco']:.2f}** no mercado **{melhor_opcao['mercado']}**.")
        
        # Tabela comparativa
        st.dataframe(dados_prod[['mercado', 'marca', 'preco', 'data']], use_container_width=True)
        
        # Gráfico de evolução se houver mais de um registro
        if len(dados_prod) > 1:
            st.subheader("Evolução do Preço")
            st.line_chart(data=dados_prod, x='data', y='preco')
    else:
        st.warning("Nenhum dado cadastrado ainda.")
