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
        df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
        df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def ler_clientes_do_csv():
    """Lê os registros do arquivo CSV convertendo todas as colunas para texto limpo."""
    inicializar_banco()
    try:
        df = pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
        df["Onesignal_ID"] = df["Onesignal_ID"].astype(str).str.strip()
        df["Preferência"] = df["Preferência"].astype(str).str.strip()
        df["Turno"] = df["Turno"].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])

def salvar_cliente_no_csv(nome, onesignal_id, whatsapp, preferencia, turno):
    """Insere ou atualiza um cliente no arquivo CSV local de forma persistente."""
    inicializar_banco()
    df_atual = ler_clientes_do_csv()
    
    # Limpa e formata o número do WhatsApp
    wpp_limpo = "".join(filter(str.isdigit, str(whatsapp)))
    if not wpp_limpo.startswith("55") and len(wpp_limpo) >= 10:
        wpp_limpo = "55" + wpp_limpo

    # Se o ID já existir, atualiza os dados; caso contrário, adiciona uma nova linha
    if onesignal_id in df_atual["Onesignal_ID"].values:
        df_atual.loc[df_atual["Onesignal_ID"] == onesignal_id, ["Nome", "WhatsApp", "Preferência", "Turno"]] = [nome, wpp_limpo, preferencia, turno]
    else:
        novo_registro = pd.DataFrame([{"Nome": nome, "Onesignal_ID": onesignal_id, "WhatsApp": wpp_limpo, "Preferência": preferencia, "Turno": turno}])
        df_atual = pd.concat([df_atual, novo_registro], ignore_index=True)
        
    df_atual.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def limpar_banco_csv():
    """Zera o arquivo CSV limpando a lista de dispositivos cadastrados."""
    df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

# ==========================================================================
# 3- MECANISMO DE DISPARO VIA ENDPOINT OFICIAL DA API REST DO ONESIGNAL
# ==========================================================================
def disparar_notificacao_push(lista_ids, titulo, message):
    """Envia requisição POST para o endpoint correto de envio de notificações do OneSignal."""
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
# 4- ROTEADOR CENTRAL: CAPTURA AUTOMÁTICA DOS DADOS DA LANDING PAGE
# ==========================================================================
params = st.query_params

# Se a URL contiver os parâmetros da Landing Page, processa o salvamento imediatamente
if "id" in params and "nome" in params:
    st.set_page_config(page_title="Cadastro Concluído!", page_icon="🥖")
    
    # Captura os dados vindos do redirecionamento do GitHub Pages
    p_nome = params.get("nome")
    p_id = params.get("id")
    p_wpp = params.get("wpp", "")
    p_pref = params.get("pref", "🥖 Pão Francês")
    p_turno = params.get("turno", "Ambos")
    
    # Grava as informações coletadas no CSV local
    salvar_cliente_no_csv(p_nome, p_id, p_wpp, p_pref, p_turno)
    
    # Exibe tela de confirmação de sucesso para o cliente no balcão
    st.balloons()
    st.markdown(
        """
        <div style='text-align: center; background-color: #1E1E1E; padding: 30px; border-radius: 12px; border: 1px solid #28a745; margin-top: 40px;'>
            <h1 style='color: #28a745; margin: 0;'>🎉 Tudo Pronto, {}!</h1>
            <p style='color: #FFF; font-size: 1.2rem; margin-top: 15px;'>Seu celular foi cadastrado com sucesso.</p>
            <p style='color: #AAA; font-size: 0.9rem;'>Você receberá um aviso na tela assim que a fornada de <b>{}</b> sair quentinha!</p>
        </div>
        """.format(p_nome, p_pref), unsafe_allow_html=True
    )
    
    # Limpa os parâmetros da URL para evitar cadastros duplicados caso a página seja recarregada
    if st.button("Concluir e Fechar", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    st.stop()

# ==========================================================================
# 5- CONFIGURAÇÃO DA INTERFACE VISUAL DO PAINEL DA COZINHA (OPERADOR)
# ==========================================================================
# Se a URL não contiver dados de cadastro, carrega por padrão o Painel da Cozinha
else:
    st.set_page_config(page_title="Painel União - Cozinha", page_icon="👨‍🍳", layout="centered")

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
    # 6- ABA GATILHO DO FORNO E FILTRAGEM DE SEGMENTOS DE CLIENTES
    # ==========================================================================
    with col_esquerda:
        st.subheader("🔥 Gatilho do Forno")
        produto_sel = st.selectbox("O que acabou de sair?", ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"])
        turno_sel = st.radio("Disparar para qual turno?", ["Manhã", "Tarde", "Todos os Turnos"], horizontal=True)
        
        titulo_alerta = f"🥖 Fornada de {produto_sel}!"
        mensagem_alerta = f"O seu {produto_sel} acabou de sair quentinho do forno! Venha buscar o seu feito na hora. 🔥☕"
        
        if st.button("Disparar Fornada 🔔", use_container_width=True):
            if len(df_clientes) > 0:
                condicao = df_clientes["Preferência"] == produto_sel
                
                if turno_sel != "Todos os Turnos":
                    condicao = condicao & (df_clientes["Turno"].isin([turno_sel, "Ambos"]))
                
                # Coleta a lista de IDs filtrada
                lista_ids = df_clientes[condicao]["Onesignal_ID"].dropna().tolist()
                
                if lista_ids:
                    sucesso = disparar_notificacao_push(lista_ids, titulo_alerta, message=mensagem_alerta)
                    if sucesso:
                        st.success(f"🎉 Notificação enviada para {len(lista_ids)} clientes do turno!")
                    else:
                        st.error("Falha técnica ao tentar enviar mensagem através da API do OneSignal.")
                else:
                    st.warning("Nenhum cliente cadastrado atende aos filtros de produto e turno selecionados.")
            else:
                st.error("O banco de dados de clientes está vazio no momento.")

    # ==========================================================================
    # 7- ABA INSCRIÇÃO MANUAL E INFORMAÇÕES DE SUPORTE
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
    # 8- PAINEL LATERAL ADMINISTRATIVO (MANUTENÇÃO DO BANCO DE DADOS)
    # ==========================================================================
    with st.sidebar:
        st.header("⚙️ Configurações do System")
        st.write("Área destinada a ações de manutenção preventiva do arquivo de dados.")
        
        if st.button("⚠️ Zerar Banco de Dados CSV", use_container_width=True):
            limpar_banco_csv()
            st.success("O banco de dados foi completamente limpado com sucesso!")
            st.rerun()
