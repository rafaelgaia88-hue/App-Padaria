import streamlit as st
import pandas as pd
import requests
import json

# ==========================================================================
#  CONEXÃO COM A API DO ONESIGNAL
# ==========================================================================
# Configurado automaticamente com as credenciais secretas do seu aplicativo
ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"
ONESIGNAL_API_KEY = "cxbxmridgetgnjqiqsq3oxaoo"


def disparar_notificacao_push(lista_ids, titulo, mensagem):
    """Função que envia o alerta simultâneo em massa para todos os IDs informados"""
    url = "https://onesignal.com"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_subscription_ids": lista_ids,  # Envia para todos da lista simultaneamente
        "headings": {"en": titulo, "pt": titulo},
        "contents": {"en": mensagem, "pt": mensagem},
        "chrome_web_badge": "https://flaticon.com"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    except Exception:
        return False


# ==========================================================================
#  2- PAINEL DE CONTROLE DO OPERADOR (PADARIA / COZINHA)
# ==========================================================================

def exibir_painel(ler_clientes_fn, limpar_banco_fn, salvar_cliente_fn=None):
    st.title("👨‍🍳 Painel de Controle - Doce Sabor")

    # Sistema de proteção por senha básica de acesso
    if not st.session_state.get("logado", False):
        st.subheader("🔒 Acesso Restrito ao Operador")
        senha = st.text_input("Digite a senha da cozinha:", type="password")

        if st.button("Acessar Painel", use_container_width=True):
            if senha == "docesabor123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")

        st.write("---")
        if st.button("⬅️ Voltar para o Cadastro Público", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        st.stop()

    st.write("💥 Bem-vindo de volta, Padeiro!")

    # Criando abas organizadas
    aba_disparo, aba_cadastro_manual = st.tabs(["🚀 Disparar Fornada", "📝 Inscrição Manual Auxiliar"])

    # Carrega a lista atual de clientes cadastrados no CSV
    lista_espera_atual = ler_clientes_fn()

    # ----------------------------------------------------------------------
    # ABA 1: DISPARO DE MENSAGENS EM MASSA (WEB PUSH)
    # ----------------------------------------------------------------------
    with aba_disparo:
        col_esquerda, col_direita = st.columns(2)

        with col_esquerda:
            st.subheader("🔥 Fornada Pronta")

            produtos_disponiveis = ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
            produto_selecionado = st.selectbox("O que acabou de sair?", produtos_disponiveis, key="prod_disparo")

            turno_disparo = st.radio("Disparar para qual turno?", ["Manhã", "Tarde", "Todos os Turnos"],
                                     horizontal=True)

            st.write("---")
            st.caption("📱 **Conteúdo do Alerta de Tela:**")

            titulo_alerta = f"🥖 Fornada de {produto_selecionado}!"
            mensagem_alerta = "Acabou de sair quentinho do forno! Venha buscar o seu feito na hora. 🔥☕"
            st.info(f"**Título:** {titulo_alerta}\n\n**Texto:** {mensagem_alerta}")

            # Lógica de Filtragem e Envio Simultâneo
            if len(lista_espera_atual) > 0:
                df = pd.DataFrame(lista_espera_atual)

                # Tratamento preventivo para garantir que a coluna exista com o nome correto
                coluna_id = "Onesignal_ID" if "Onesignal_ID" in df.columns else df.columns[1]

                df["Preferência"] = df["Preferência"].astype(str).str.strip()
                condicao = df["Preferência"] == produto_selecionado

                if turno_disparo != "Todos os Turnos":
                    condicao = condicao & (df["Turno"].isin([turno_disparo, "Ambos"]))

                clientes_filtrados = df[condicao]
                lista_ids_envio = clientes_filtrados[coluna_id].dropna().tolist()

                st.write("---")

                if len(lista_ids_envio) > 0:
                    st.success(f"📢 {len(lista_ids_envio)} aparelhos receberão este aviso instantaneamente!")

                    # O BOTÃO ÚNICO DE UM CLIQUE REAL
                    if st.button("🚀 ENVIAR NOTIFICAÇÃO EM MASSA AGORA", use_container_width=True, type="primary"):
                        with st.spinner("Enviando sinais para os celulares dos clientes..."):
                            sucesso = disparar_notificacao_push(lista_ids_envio, titulo_alerta, mensagem_alerta)
                            if sucesso:
                                st.success("✨ Alerta enviado com sucesso para todos os aparelhos conectados!")
                                st.balloons()
                            else:
                                st.error("Falha ao enviar. Verifique se as chaves da API do OneSignal estão corretas.")
                else:
                    st.warning(f"Nenhum aparelho ativo esperando {produto_selecionado} neste turno.")
            else:
                st.warning("Nenhum cliente cadastrado na lista.")

        with col_direita:
            st.subheader("📋 Lista de Aparelhos Conectados")
            if len(lista_espera_atual) > 0:
                st.dataframe(pd.DataFrame(lista_espera_atual), use_container_width=True, hide_index=True)
                if st.button("❌ Limpar Fila (Zerar Banco)", use_container_width=True):
                    limpar_banco_fn()
                    st.rerun()
            else:
                st.info("Nenhum aparelho cadastrado na fila.")

    # ----------------------------------------------------------------------
    # ABA 2: INFORMAÇÕES DE CADASTRO MANUAL
    # ----------------------------------------------------------------------
    with aba_cadastro_manual:
        st.subheader("📝 Cadastro de Balcão com Web Push")
        st.warning(
            "Como o sistema Web Push funciona enviando sinais direto para as telas dos navegadores físicos, "
            "não é possível digitar manualmente o ID de um aparelho de fora.\n\n"
            "👉 **O que fazer no Balcão?** Quando um cliente quiser ser cadastrado, peça para ele apontar a câmera "
            "do celular para o QR Code uma única vez e clicar em 'Permitir'. O aparelho dele ficará guardado permanentemente "
            "na lista do sistema!"
        )

    st.write("---")
    if st.button("🚪 Sair do Painel", use_container_width=True):
        st.session_state.logado = False
        st.query_params.clear()
        st.rerun()
