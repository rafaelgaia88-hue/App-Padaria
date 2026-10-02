import streamlit as st
import streamlit.components.v1 as components

# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (POP-UP AUTOMÁTICO APÓS 2 SEGUNDOS)
# ==========================================================================

def exibir_cadastro(salvar_cliente_fn):
    st.markdown(
        """
        <div style='text-align: center; padding: 10px 0px;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🥖 Padaria Doce Sabor</h1>
            <p style='font-size: 1.2rem; color: #FFA500; font-weight: bold; margin-top: 5px;'>
                🔥 Avisos Direto na sua Tela!
            </p>
            <p style='font-size: 1rem; color: #888; margin-top: -10px;'>
                Inscreva-se abaixo para receber um alerta instantâneo assim que o pão sair quentinho.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("") # Espaçador técnico

    ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"

    # JavaScript Inteligente: Espera 2 segundos e dispara o pop-up sozinho
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
        
        // Função para rodar em segundo plano
        async function verificarEPedirPermissao() {{
            let permissao = await OneSignal.Notifications.permission;
            
            // Se ainda não foi concedida nem negada, pede automaticamente após o delay
            if (!permissao || permissao === "default") {{
                setTimeout(async () => {{
                    await OneSignal.Notifications.requestPermission();
                    enviarTokenParaStreamlit();
                }}, 2000); // 2000 milissegundos = 2 segundos de espera
            }} else {{
                enviarTokenParaStreamlit();
            }}
        }}

        async function enviarTokenParaStreamlit() {{
            let subscriptionId = OneSignal.User.PushSubscription.id;
            if (subscriptionId) {{
                window.parent.postMessage({{
                    type: 'streamlit:set_query_params',
                    queryParams: {{ 'device_id': subscriptionId }}
                }}, '*');
            }}
        }}

        // Executa a checagem assim que o script carregar
        verificarEPedirPermissao();
      }});
    </script>
    """
    components.html(js_onesignal, height=0, width=0)

    # Captura o ID do dispositivo enviado pelo JavaScript
    device_id_capturado = st.query_params.get("device_id", None)

    # FORMULÁRIO DE CADASTRO LIMPO
    with st.form("form_cliente_direto", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")
        
        # Feedback visual sutil dentro do formulário
        if device_id_capturado:
            st.success("✅ Seu celular está conectado e pronto para receber os avisos!")
        else:
            st.warning("🔔 Por favor, clique em 'Permitir' no aviso que aparecerá na sua tela.")

        produto = st.selectbox(
            "Qual fornada quer acompanhar?",
            ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
        )

        turno = st.selectbox(
            "Qual horário você costuma vir à padaria?",
            ["Manhã", "Tarde", "Ambos"]
        )

        st.write("") 
        botao_cadastrar = st.form_submit_button("Quero Receber os Alertas! 🔔", use_container_width=True)

    # Lógica de Salvamento
    if botao_cadastrar:
        if nome:
            if not device_id_capturado:
                st.error("⚠️ O navegador ainda não liberou seu aparelho. Garanta que clicou em 'Permitir' no pop-up do site.")
            else:
                salvar_cliente_fn(nome, device_id_capturado, produto, turno)
                st.balloons()
                st.success(f"🎉 Perfeito, {nome}! Você receberá um alerta direto na tela do celular assim que sair uma nova fornada de {produto}!")
        else:
            st.error("⚠️ Por favor, preencha o seu Nome para continuar.")

    # Rodapé discreto para navegação do operador
    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params["tela"] = "operador"
        st.rerun()
