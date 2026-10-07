import streamlit as st
import pandas as pd
import os
import requests
import json

# ==========================================================================
# 1- DEFINIÇÃO DE CREDENCIAIS E VARIÁVEIS GLOBAIS DO ONESIGNAL
# ==========================================================================
ARQUIVO_CSV = "clientes_padaria.csv"
ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"
ONESIGNAL_API_KEY = "cxbxmridgetgnjqiqsq3oxaoo"

# ==========================================================================
# 2- GERENCIAMENTO E INICIALIZAÇÃO DO BANCO DE DADOS LOCAL
# ==========================================================================
def inicializar_banco():
    """Garante a existência do arquivo CSV com o cabeçalho padronizado."""
    if not os.path.exists(ARQUIVO_CSV) or os.stat(ARQUIVO_CSV).st_size == 0:
        # Padronizado estritamente para 'Onesignal_ID' combinando com a leitura do painel
        df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
        df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def ler_clientes_do_csv():
    """Lê os registros do arquivo CSV convertendo todas as colunas para texto limpo."""
    inicializar_banco()
    try:
        df = pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
        # Força os tipos de dados para evitar quebras durante a filtragem do operador
        df["Onesignal_ID"] = df["Onesignal_ID"].astype(str).str.strip()
        df["Preferência"] = df["Preferência"].astype(str).str.strip()
        df["Turno"] = df["Turno"].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])

def limpar_banco_csv():
    """Zera o arquivo CSV limpando a lista de dispositivos cadastrados."""
    df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

# ==========================================================================
# 3- MECANISMO DE DISPARO VIA ENDPOINT OFICIAL DA API REST DO ONESIGNAL
# ==========================================================================
def disparar_notificacao_push(lista_ids, titulo, message):
    """Envia requisição POST para o endpoint correto de envio de notificações do OneSignal."""
    # CORREÇÃO: Alterado de 'https://onesignal.com' para a rota oficial da API v1
    url = "https://onesignal.com"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_subscription_ids": lista_ids,
        "headings": {"en": titulo, "pt": titulo},
        "contents": {"en": message, "pt": message}
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    except Exception:
        return False

# ==========================================================================
# 4- CONFIGURAÇÃO DA INTERFACE VISUAL DO PAINEL DA COZINHA (OPERADOR)
# ==========================================================================
st.set_page_config(page_title="Painel União - Cozinha", page_icon="👨‍🍳", layout="centered")

# Inicialização da variável de controle de sessão
if "logado" not in st.session_state:
    st.session_state.logado = False

# Fluxo de autenticação restrita do operador da cozinha
if not st.session_state.logado:
    st.subheader("🔒 Acesso Restrito - Padaria Doce Sabor")
    senha = st.text_input("Digite a senha da cozinha:", type="password")
    if st.button("Acessar Painel", use_container_width=True):
        if senha == "docesabor123":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# Cabeçalho principal da aplicação administrativa
st.title("👨‍🍳 Painel de Controle da Cozinha")
df_clientes = ler_clientes_do_csv()

# Divisão da tela em duas colunas funcionais
col_esquerda, col_direita = st.columns(2)

# ==========================================================================
# 5- ABA GATILHO DO FORNO E FILTRAGEM DE SEGMENTOS DE CLIENTES
# ==========================================================================
with col_esquerda:
    st.subheader("🔥 Gatilho do Forno")
    produto_sel = st.selectbox("O que acabou de sair?", ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"])
    turno_sel = st.radio("Disparar para qual turno?", ["Manhã", "Tarde", "Todos os Turnos"], horizontal=True)
    
    titulo_alerta = f"🥖 Fornada de {produto_sel}!"
    mensagem_alerta = f"O seu {produto_sel} acabou de sair quentinho do forno! Venha buscar o seu feito na hora. 🔥☕"
    
    if st.button("Disparar Fornada 🔔", use_container_width=True):
        if len(df_clientes) > 0:
            # Aplicação dos filtros baseados na preferência do produto selecionado
            condicao = df_clientes["Preferência"] == produto_sel
            
            # Aplicação secundária dos filtros com base no turno escolhido
            if turno_sel != "Todos os Turnos":
                condicao = condicao & (df_clientes["Turno"].isin([turno_sel, "Ambos"]))
            
            # CORREÇÃO: Recuperação dos IDs corrigindo o corte de sintaxe original
            lista_ids = df_clientes[condicao]["Onesignal_ID"].dropna().tolist()
            
            if lista_ids:
                sucesso = disparar_notificacao_push(lista_ids, titulo_alerta, mensagem_alerta)
                if sucesso:
                    st.success(f"🎉 Notificação enviada para {len(lista_ids)} clientes do turno!")
                else:
                    st.error("Falha técnica ao tentar enviar mensagem através da API do OneSignal.")
            else:
                st.warning("Nenhum cliente cadastrado atende aos filtros de produto e turno selecionados.")
        else:
            st.error("O banco de dados de clientes está vazio no momento.")

# ==========================================================================
# 6- ABA INSCRIÇÃO MANUAL E INFORMAÇÕES DE SUPORTE
# ==========================================================================
with col_direita:
    st.subheader("📋 Status da Base")
    st.metric(label="Total de Clientes Cadastrados", value=len(df_clientes))
    
    with st.expander("Visualizar Lista de Dispositivos Ativos"):
        if len(df_clientes) > 0:
            st.dataframe(df_clientes[["Nome", "Preferência", "Turno"]])
        else:
            st.caption("Nenhum registro encontrado no arquivo clientes_padaria.csv.")

# ==========================================================================
# 7- PAINEL LATERAL ADMINISTRATIVO (MANUTENÇÃO DO BANCO DE DADOS)
# ==========================================================================
with st.sidebar:
    st.header("⚙️ Configurações do Sistema")
    st.write("Área destinada a ações de manutenção preventiva do arquivo de dados.")
    
    # Botão de segurança para reinicialização completa da base de dados local
    if st.button("⚠️ Zerar Banco de Dados CSV", use_container_width=True):
        limpar_banco_csv()
        st.success("O banco de dados foi completamente limpado com sucesso!")
        st.rerun()
