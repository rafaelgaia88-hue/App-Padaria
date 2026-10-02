import streamlit as st
import pandas as pd
import os

# Importando as visualizações criadas dentro da pasta views conforme sua imagem
from views.cadastro import exibir_cadastro
from views.Painel_Operador import exibir_painel

# ==========================================================================
#  3- CONFIGURAÇÃO DA PÁGINA CENTRAL
# ==========================================================================
st.set_page_config(
    page_title="Padaria Doce Sabor",
    page_icon="🥖",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.markdown("<style>[data-testid='collapsedControl'] {display: none;}</style>", unsafe_allow_html=True)

# ==========================================================================
#  4- CONEXÃO COM BANCO DE DADOS LOCAL (ARQUIVO CSV)
# ==========================================================================
ARQUIVO_CSV = "clientes_padaria.csv"

def inicializar_banco():
    if not os.path.exists(ARQUIVO_CSV):
        df = pd.DataFrame(columns=["Nome", "WhatsApp", "Preferência", "Turno"])
        df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def salvar_cliente_no_csv(nome, whatsapp, preferencia, turno):
    inicializar_banco()
    novo_registro = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp, "Preferência": preferencia, "Turno": turno}])
    novo_registro.to_csv(ARQUIVO_CSV, mode='a', header=False, index=False, encoding="utf-8")

def ler_clientes_do_csv():
    inicializar_banco()
    try:
        df = pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
        return df.to_dict(orient="records")
    except pd.errors.EmptyDataError:
        return []

def limpar_banco_csv():
    df = pd.DataFrame(columns=["Nome", "WhatsApp", "Preferência", "Turno"])
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

if "logado" not in st.session_state:
    st.session_state.logado = False

# ==========================================================================
#  5- ROTEADOR DE NAVEGAÇÃO
# ==========================================================================
params = st.query_params
if params.get("tela") == "operador":
    # AJUSTE AQUI: Adicionado 'salvar_cliente_no_csv' como o terceiro argumento
    exibir_painel(ler_clientes_do_csv, limpar_banco_csv, salvar_cliente_no_csv)
else:
    exibir_cadastro(salvar_cliente_no_csv)

