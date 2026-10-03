import streamlit as st
import streamlit.components.v1 as components

# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (SOLUÇÃO CORRIGIDA)
# ==========================================================================

def exibir_cadastro(salvar_cliente_fn):
    # Banner elegante da padaria artesanal
    st.markdown(
        """
        <div style='text-align: center; background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #FFA500; margin-bottom: 20px;'>
            <span style='font-size: 3.5rem;'>🥖</span>
            <h1 style='font-size: 2.2rem; color: #FFF; margin: 10px 0 0 0; font-family: sans-serif;'>Seja Bem-Vindo!</h1>
            <p style='font-size: 1.2rem; color: #FFA500; font-weight: bold; margin: 5px 0 0 0;'>
                Padaria Doce Sabor
            </p>
            <p style='font-size: 0.95rem; color: #AAA; margin: 10px 0 0 0; line-height: 1.4;'>
                Inscreva-se para receber um aviso instantâneo direto na sua tela assim que o pãozinho sair quentinho do forno!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"
    device_id_capturado = st.query_params.get("device_id", None)

    # FORMULÁRIO DE CADASTRO
    with st.form("form_cliente_direto", clear_on_submit=False):
        nome = st.text_input("Seu Nome *:")
        whatsapp = st.text_input("Seu WhatsApp (com DDD) *:", placeholder="Ex: 11999998888")

        # Ajustado para "Preferência" para bater exatamente com as colunas do seu main.py
        preferencia = st.selectbox(
            "Qual fornada quer acompanhar?",
            ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
        )

        turno = st.selectbox(
            "Qual horário você costuma vir à padaria?",
            ["Manhã", "Tarde", "Ambos"]
        )

        st.write("") 
        
        concordou_termos = st.checkbox(
            "Li e concordo com os termos de uso e aceito receber as notificações de pão quentinho.",
            value=True if device_id_capturado else False
        )

        # Status dinâmico integrado ao layout escuro
        if device_id_capturado:
            st.success("✅ Seu dispositivo foi reconhecido com sucesso!")
        else:
            st.info("🔔 Para validar, você precisa usar o botão de ativação de notificações abaixo.")
            
            # SOLUÇÃO DA PONTE INTEGRADA: Junta o SDK da CDN oficial e resolve o escopo de execução do botão
            ponte_onesignal_html = f"""
            <script src="https://onesignal.com" async></script>
            <script>
              window.OneSignal = window.OneSignal || [];
              OneSignal.push(async function() {{
                await OneSignal.init({{
                  appId: "{ONESIGNAL_APP_ID}",
                  allowLocalhostAsSecureOrigin: true
                }});
              }});
              
              async function dispararPromptNotificacao() {{
                try {{
                    await OneSignal.Notifications.requestPermission();
                    
                    let checaToken = setInterval(async () => {{
                        let subscriptionId = OneSignal.User.PushSubscription.id;
                        if (subscriptionId) {{
                            clearInterval(checaToken);
                            window.parent.postMessage({{
                                type: 'streamlit:set_query_params',
                                queryParams: {{ 'device_id': subscriptionId }}
                            }}, '*');
                        }}
                    }}, 1000);
                }} catch(e) {{
                    console.error("Erro na ponte de permissão:", e);
                }}
              }}
            </script>
            <div style='text-align: center;'>
                <button type='button' onclick='dispararPromptNotificacao()' style='width: 100%; background-color: #FFA500; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 14px; box-shadow: 0px 4px 6px rgba(0,0,0,0.2); font-family: sans-serif;'>
                    👉 CLIQUE AQUI PARA AUTORIZAR NOTIFICAÇÕES 🔔
                </button>
            </div>
            """
            components.html(ponte_onesignal_html, height=55)

        st.write("") 
        botao_cadastrar = st.form_submit_button("Me Avise Quando Sair! 🔔", use_container_width=True)

    # VALIDAÇÃO DO SUBMIT
    if botao_cadastrar:
        if not nome.strip() or not whatsapp.strip():
            st.error("⚠️ Erro: Os campos de Nome e WhatsApp são obrigatórios! Preencha-os antes de continuar.")
        elif not concordou_termos:
            st.error("⚠️ Erro: Você precisa aceitar as condições marcando o checkbox dos termos.")
        elif not device_id_capturado:
            st.error("⚠️ Erro: Falta autorização técnica. Clique primeiro no botão laranja 'AUTORIZAR NOTIFICAÇÕES' e dê 'Permitir'.")
        else:
            wpp_limpo = "".join(filter(str.isdigit, whatsapp))
            if len(wpp_limpo) < 10:
                st.error("⚠️ Por favor, informe um número de WhatsApp válido com o DDD.")
            else:
                if not wpp_limpo.startswith("55"):
                    wpp_limpo = "55" + wpp_limpo

                # Variáveis enviadas batendo perfeitamente com a assinatura da função no seu main.py
                salvar_cliente_fn(nome, device_id_capturado, wpp_limpo, preferencia, turno)
                st.balloons()
                st.success(f"🎉 Perfeito, {nome}! Cadastro realizado. Avisaremos você direto na tela!")

    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params.clear() # Limpa o device_id ao ir para a tela do operador
        st.query_params["tela"] = "operador"
        st.rerun()
