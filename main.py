import streamlit as st
import pandas as pd
import os

# Importando as visualizações criadas dentro da pasta views conforme sua imagem
from views.cadastro import exibir_cadastro
from views.Painel_Operador import exibir_painel

ARQUIVO_CSV = "clientes_padaria.csv"

def inicializar_banco():
    if not os.path.exists(ARQUIVO_CSV):
        # Banco completo contendo tanto o ID da Tela quanto o WhatsApp do cliente
        df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
        df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def salvar_cliente_no_csv(nome, onesignal_id, whatsapp, preferencia, turno):
    inicializar_banco()
    df_atual = pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
    
    # Se o mesmo aparelho já existir, atualiza os dados para não duplicar envios
    if onesignal_id in df_atual["Onesignal_ID"].values:
        df_atual.loc[df_atual["Onesignal_ID"] == onesignal_id, ["Nome", "WhatsApp", "Preferência", "Turno"]] = [nome, whatsapp, preferencia, turno]
        df_atual.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")
    else:
        # Adiciona o novo registro completo
        novo_registro = pd.DataFrame([{"Nome": nome, "Onesignal_ID": onesignal_id, "WhatsApp": whatsapp, "Preferência": preferencia, "Turno": turno}])
        novo_registro.to_csv(ARQUIVO_CSV, mode='a', header=False, index=False, encoding="utf-8")

def ler_clientes_do_csv():
    inicializar_banco()
    try:
        df = pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
        return df.to_dict(orient="records")
    except pd.errors.EmptyDataError:
        return []

def limpar_banco_csv():
    df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

if "logado" not in st.session_state:
    st.session_state.logado = False

# ==========================================================================
#  5- ROTEADOR DE NAVEGAÇÃO
# ==========================================================================
params = st.query_params
if params.get("tela") == "operador":
    exibir_painel(ler_clientes_do_csv, limpar_banco_csv, salvar_cliente_no_csv)
else:
    exibir_cadastro(salvar_cliente_no_csv)
