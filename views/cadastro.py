import streamlit as st
import streamlit.components.v1 as components


# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (VERSÃO WEB PUSH CONFIGURADA)
# ==========================================================================

def exibir_cadastro(salvar_cliente_fn):
    # Cabeçalho estilizado sem dependência de links externos de imagem
    st.markdown(
        """
        <div style='text-align: center; padding: 10px 0px;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🥖 Padaria Doce Sabor</h1>
            <p style='font-size: 1.2rem; color: #FFA500; font-weight: bold; margin-top: 5px;'>
                🔥 Avisos Direto na sua Tela!
            </p>
            <p style='font-size: 1rem; color: #888; margin-top: -10px;'>
                Ative as notificações para receber um alerta instantâneo assim que o pão sair quentinho.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")  # Espaçador técnico

    # CONFIGURAÇÃO DE CHAVE CONFIGURADA AUTOMATICAMENTE CONFORME SEU PAINEL ONESIGNAL
    ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"

    # Injeção do Script JavaScript do OneSignal para capturar o ID do celular
    js_onesignal = f"""
    <script src="https://onesignal.com" async></script>
    <script>
      window.OneSignal = window.OneSignal || [];
      OneSignal.push(async function() {{
        await OneSignal.init({{
          appId: "{ONESIGNAL_APP_ID}",
          safari_web_id: "optional_safari_id",
          notifyButton: {{
            enable: false,
          }},
        }});

        // Solicita a permissão de notificação na tela do cliente automaticamente
        await OneSignal.Notifications.requestPermission();

        // Pega o ID único do dispositivo do cliente
        let subscriptionId = OneSignal.User.PushSubscription.id;
        if (subscriptionId) {{
            // Devolve o ID capturado para a URL do Streamlit
            window.parent.postMessage({{
                type: 'streamlit:set_query_params',
                queryParams: {{ 'device_id': subscriptionId }}
            }}, '*');
        }}
      }});
    </script>
    """
    # Executa o script JavaScript oculto na página
    components.html(js_onesignal, height=0, width=0)

    # Lê o ID do aparelho que o JavaScript enviou para a URL
    device_id_capturado = st.query_params.get("device_id", None)

    # Formulário simplificado e elegante (Sem campo de WhatsApp, usando a tela)
    with st.form("form_cliente_direto", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")

        # Feedback visual para o cliente saber se o celular dele ativou corretamente
        if device_id_capturado:
            st.success("✅ Seu celular está conectado e pronto para receber os avisos!")
        else:
            st.warning("🔔 Por favor, clique em 'Permitir' no aviso que apareceu no seu navegador.")

        produto = st.selectbox(
            "Qual fornada quer acompanhar?",
            ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
        )

        turno = st.selectbox(
            "Qual horário você costuma vir à padaria?",
            ["Manhã", "Tarde", "Ambos"]
        )

        st.write("")  # Espaçador interno do formulário
        botao = st.form_submit_button("Quero Receber os Alertas! 🔔", use_container_width=True)

    if botao:
        if nome:
            if not device_id_capturado:
                st.error(
                    "⚠️ Não conseguimos registrar seu celular. Garanta que você aceitou as notificações no pop-up do navegador.")
            else:
                # Salva no arquivo CSV passando o Nome e o ID do OneSignal para os disparos simultâneos
                salvar_cliente_fn(nome, device_id_capturado, produto, turno)

                st.balloons()
                st.success(
                    f"🎉 Perfeito, {nome}! Você receberá um alerta direto na tela do celular assim que sair uma nova fornada de {produto}!")
        else:
            st.error("⚠️ Por favor, preencha o seu Nome para continuar.")

    # Rodapé discreto para navegação do operador
    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params["tela"] = "operador"
        st.rerun()
