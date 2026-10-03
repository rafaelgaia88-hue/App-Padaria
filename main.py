import streamlit as st
import pandas as pd
import os
import requests
import json
import shutil
import streamlit.components.v1 as components

# --- INJEÇÃO AUTOMÁTICA E COPIAGEM DO SERVICE WORKER ---
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

# --- CONFIGURAÇÃO DO BANCO DE DADOS CSV ---
ARQUIVO_CSV = "clientes_padaria.csv"
ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"
ONESIGNAL_API_KEY = "cxbxmridgetgnjqiqsq3oxaoo"
SAFARI_WEB_ID = "safari.web.id.onesignal.auto.2b467c5d-2ccd-4ce0-a57b-cb7ab9cfd0c8"

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
    wpp_limpo = "".join(filter(str.isdigit, str(whatsapp)))
    if not wpp_limpo.startswith("55") and len(wpp_limpo) >= 10:
        wpp_limpo = "55" + wpp_limpo

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
#  ROTEADOR CENTRAL DO SISTEMA UNIFICADO
# ==========================================================================
params = st.query_params

# VISÃO A: CADASTRO PÚBLICO DO CLIENTE (EXECUTA DIRETO NO STREAMLIT)
if params.get("tela") != "operador":
    st.set_page_config(page_title="Pão Quentinho - Inscrição", page_icon="🥖")
    
    # Injeção oficial do OneSignal via Slidedown nativo (Não sofre bloqueio de domínio)
    onesignal_js = f"""
    <script src="https://onesignal.com" defer></script>
    <script>
      window.OneSignalDeferred = window.OneSignalDeferred || [];
      window.OneSignalDeferred.push(async function(OneSignal) {{
        await OneSignal.init({{
          appId: "{ONESIGNAL_APP_ID}",
          safari_web_id: "{SAFARI_WEB_ID}",
          allowLocalhostAsSecureOrigin: true
        }});
        
        // Dispara o Slidedown Prompt nativo automaticamente na tela do usuário
        await OneSignal.Notifications.requestPermission();
        
        setInterval(async () => {{
            let subId = OneSignal.User.PushSubscription.id;
            if (subId) {{
                window.parent.postMessage({{
                    type: 'streamlit:set_query_params',
                    queryParams: {{ 'device_id': subId }}
                }}, '*');
            }}
        }}, 1500);
      }});
    </script>
    """
    components.html(onesignal_js, height=0, width=0)
    
    st.markdown(
        """
        <div style='text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 12px; border: 1px solid #FFA500; margin-bottom: 20px;'>
            <h1 style='color: #FFF; margin: 0;'>🥖 Seja Bem-Vindo!</h1>
            <p style='color: #FFA500; font-weight: bold;'>Padaria Doce Sabor</p>
            <p style='color: #AAA; font-size: 0.9rem;'>Inscreva-se para receber avisos de fornadas direto no celular!</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    id_capturado = params.get("device_id", None)
    
    with st.form("form_cliente_final"):
        nome = st.text_input("Seu Nome *:")
        whatsapp = st.text_input("Seu WhatsApp (com DDD) *:")
        preferencia = st.selectbox("Qual fornada quer acompanhar?", ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"])
        turno = st.selectbox("Qual horário você costuma vir à padaria?", ["Manhã", "Tarde", "Ambos"])
        
        if id_capturado:
            st.success("✅ Seu dispositivo foi reconhecido com sucesso!")
        else:
            st.info("🔔 Aguarde o pop-up do navegador aparecer na tela e clique em 'Permitir'.")
            
        cadastrar = st.form_submit_button("Me Avise Quando Sair! 🔔", use_container_width=True)
        
        if cadastrar:
            if not nome.strip() or not whatsapp.strip():
                st.error("Preencha todos os campos obrigatórios!")
            elif not id_capturado:
                st.error("Falta autorização técnica. Certifique-se de dar 'Permitir' no aviso do navegador.")
            else:
                salvar_cliente_no_csv(nome, id_capturado, whatsapp, preferencia, turno)
                st.balloons()
                st.success("🎉 Perfeito! Cadastro salvo com sucesso.")
                
    st.write("---")
    if st.button("🔐 Painel Interno", use_container_width=True):
        st.query_params.clear()
        st.query_params["tela"] = "operador"
        st.rerun()

# VISÃO B: PAINEL DE CONTROLE DA COZINHA (OPERADOR)
else:
    st.set_page_config(page_title="Painel União - Cozinha", page_icon="👨‍🍳", layout="centered")
    if "logado" not in st.session_state: st.session_state.logado = False
    
    if not st.session_state.logado:
        st.subheader("🔒 Acesso Restrito - Padaria Doce Sabor")
        senha = st.text_input("Digite a senha da cozinha:", type="password")
        if st.button("Acessar Painel", use_container_width=True):
            if senha == "docesabor123":
                st.session_state.logado = True
                st.rerun()
            else: st.error("Senha incorreta!")
        st.stop()

    st.title("👨‍🍳 Painel de Controle da Cozinha")
    df_clientes = ler_clientes_do_csv()
    col_esquerda, col_direita = st.columns(2)

    with col_esquerda:
        st.subheader("🔥 Gatilho do Forno")
        produto_sel = st.selectbox("O que acabou de sair?", ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"])
        turno_sel = st.radio("Disparar para qual turno?", ["Manhã", "Tarde", "Todos os Turnos"], horizontal=True)
        
        titulo_alerta = f"🥖 Fornada de {produto_sel}!"
        mensagem_alerta = "Acabou de sair quentinho do forno! Venha buscar o seu feito na hora. 🔥☕"
        
        if len(df_clientes) > 0:
            df_clientes["Preferência"] = df_clientes["Preferência"].astype(str).str.strip()
            condicao = df_clientes["Preferência"] == produto_sel
            if turno_sel != "Todos os Turnos":
                condicao = condicao & (df_clientes["Turno"].isin([turno_sel, "Ambos"]))
            lista_ids = df_clientes[condicao]["Onesignal_ID"].dropna().tolist()
            
            if len(lista_ids) > 0:
                st.success(f"📢 {len(lista_ids)} dispositivos vão receber esse aviso!")
                if st.button("🚀 DISPARAR NOTIFICAÇÃO AGORA", type="primary", use_container_width=True):
                    if disparar_notificacao_push(lista_ids, titulo_alerta, mensagem_alerta):
                        st.success("✨ Notificação enviada!")
                        st.balloons()
            else: st.warning("Ninguém esperando por este produto neste turno.")
        else: st.warning("Nenhum cliente cadastrado.")

    with col_direita:
        st.subheader("📋 Clientes Conectados")
        if len(df_clientes) > 0:
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
            if st.button("❌ Zerar Lista", use_container_width=True):
                limpar_banco_csv()
                st.rerun()
        else: st.info("Lista vazia.")
