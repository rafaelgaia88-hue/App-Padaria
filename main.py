import streamlit as st
import pandas as pd
import os
import requests
import json
import shutil

# --- INJEÇÃO AUTOMÁTICA DO SERVICE WORKER NO STREAMLIT ---
def injetar_service_worker():
    try:
        pagedir = os.path.dirname(st.__file__)
        static_dir = os.path.join(pagedir, "static")
        arquivo_origem = "OneSignalSDKWorker.js"
        arquivo_destino = os.path.join(static_dir, "OneSignalSDKWorker.js")
        if os.path.exists(arquivo_origem) and not os.path.exists(arquivo_destino):
            shutil.copy(arquivo_origem, arquivo_destino)
    except Exception as e:
        print(f"Erro ao injetar o Service Worker: {e}")

injetar_service_worker()

# --- CONFIGURAÇÃO GLOBAL DO ARQUIVO ---
ARQUIVO_CSV = "clientes_padaria.csv"
ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"
ONESIGNAL_API_KEY = "cxbxmridgetgnjqiqsq3oxaoo"

def inicializar_banco():
    if not os.path.exists(ARQUIVO_CSV) or os.stat(ARQUIVO_CSV).st_size == 0:
        df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
        df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def ler_clientes_do_csv():
    inicializar_banco()
    try:
        return pd.read_csv(ARQUIVO_CSV, encoding="utf-8")
    except Exception:
        return pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])

def salvar_cliente_no_csv(nome, onesignal_id, whatsapp, preferencia, turno):
    inicializar_banco()
    df_atual = ler_clientes_do_csv()
    
    # Remove qualquer caractere que não seja número do WhatsApp
    wpp_limpo = "".join(filter(str.isdigit, str(whatsapp)))
    if not wpp_limpo.startswith("55") and len(wpp_limpo) >= 10:
        wpp_limpo = "55" + wpp_limpo

    # Se o ID já existir, atualiza. Se não, adiciona
    if onesignal_id in df_atual["Onesignal_ID"].values:
        df_atual.loc[df_atual["Onesignal_ID"] == onesignal_id, ["Nome", "WhatsApp", "Preferência", "Turno"]] = [nome, wpp_limpo, preferencia, turno]
    else:
        novo_registro = pd.DataFrame([{"Nome": nome, "Onesignal_ID": onesignal_id, "WhatsApp": wpp_limpo, "Preferência": preferencia, "Turno": turno}])
        df_atual = pd.concat([df_atual, novo_registro], ignore_index=True)
        
    df_atual.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def limpar_banco_csv():
    df = pd.DataFrame(columns=["Nome", "Onesignal_ID", "WhatsApp", "Preferência", "Turno"])
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8")

def disparar_notificacao_push(lista_ids, titulo, message):
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
#  REGRAS DE ROTEAMENTO (O QUE MOSTRAR NA TELA)
# ==========================================================================
params = st.query_params

# CASO 1: Captura o clique vindo do PWA do cliente e salva no CSV
if params.get("acao") == "cadastrar":
    st.set_page_config(page_title="Cadastro Realizado!", page_icon="🎉")
    salvar_cliente_no_csv(
        nome=params.get("nome"),
        onesignal_id=params.get("id"),
        whatsapp=params.get("wpp"),
        preferencia=params.get("pref"),
        turno=params.get("turno")
    )
    st.balloons()
    st.markdown(
        """
        <div style='text-align: center; margin-top: 50px;'>
            <span style='font-size: 5rem;'>🎉</span>
            <h2 style='color: #28a745;'>Cadastro Realizado com Sucesso!</h2>
            <p style='font-size: 1.2rem; color: #555;'>Você já está na lista. Pode fechar esta página e aguardar o aviso de pão quentinho direto no seu celular!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.stop()

# CASO 2: Se não for um cadastro automático, abre o Painel do Operador normalmente
st.set_page_config(page_title="Painel União - Cozinha", page_icon="👨‍🍳", layout="centered")

if "logado" not in st.session_state:
    st.session_state.logado = False

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

# --- INTERFACE OFICIAL DO PAINEL DO OPERADOR ---
st.title("👨‍🍳 Painel de Controle da Cozinha")
df_clientes = ler_clientes_do_csv()

col_esquerda, col_direita = st.columns(2)

with col_esquerda:
    st.subheader("🔥 Gatilho do Forno")
    produtos = ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
    produto_sel = st.selectbox("O que acabou de sair?", produtos)
    turno_sel = st.radio("Disparar para qual turno?", ["Manhã", "Tarde", "Todos os Turnos"], horizontal=True)
    
    st.write("---")
    titulo_alerta = f"🥖 Fornada de {produto_sel}!"
    mensagem_alerta = "Acabou de sair quentinho do forno! Venha buscar o seu feito na hora. 🔥☕"
    st.info(f"**Preview Alerta:**\n\n**Título:** {titulo_alerta}\n**Mensagem:** {mensagem_alerta}")

    if len(df_clientes) > 0:
        df_clientes["Preferência"] = df_clientes["Preferência"].astype(str).str.strip()
        condicao = df_clientes["Preferência"] == produto_sel
        
        if turno_sel != "Todos os Turnos":
            condicao = condicao & (df_clientes["Turno"].isin([turno_sel, "Ambos"]))
            
        clientes_filtrados = df_clientes[condicao]
        lista_ids = clientes_filtrados["Onesignal_ID"].dropna().tolist()
        
        if len(lista_ids) > 0:
            st.success(f"📢 {len(lista_ids)} dispositivos vão receber esse aviso!")
            if st.button("🚀 DISPARAR NOTIFICAÇÃO AGORA", type="primary", use_container_width=True):
                with st.spinner("Disparando sinais de push..."):
                    if disparar_notificacao_push(lista_ids, titulo_alerta, mensagem_alerta):
                        st.success("✨ Notificação enviada para todos com sucesso!")
                        st.balloons()
                    else:
                        st.error("Falha ao enviar através do OneSignal.")
        else:
            st.warning(f"Ninguém esperando por {produto_sel} neste turno.")
    else:
        st.warning("Nenhum cliente cadastrado na base de dados ainda.")

with col_direita:
    st.subheader("📋 Clientes Conectados")
    if len(df_clientes) > 0:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        if st.button("❌ Zerar Lista de Clientes", use_container_width=True):
            limpar_banco_csv()
            st.rerun()
    else:
        st.info("Lista vazia.")
