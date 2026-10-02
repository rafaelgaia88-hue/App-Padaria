import streamlit as st
import streamlit.components.v1 as components

# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (VERSÃO SOFT PROMPT)
# ==========================================================================

def exibir_cadastro(salvar_cliente_fn):
    st.markdown(
        """
        <div style='text-align: center; padding: 10px 0px;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🥖 Padaria Doce e Sabor</h1>
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

    st.write("") # Espaçador técnico

    ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"

    # JavaScript Otimizado: Inicializa o OneSignal e cria a função de gatilho manual
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
        
        // Função que será chamada quando o usuário clicar no botão do Streamlit
        window.ativarNotificacoes = async function() {{
            await OneSignal.Notifications.requestPermission();
            let subscriptionId = OneSignal.User.PushSubscription.id;
            if (subscriptionId) {{
                window.parent.postMessage({{
                    type: 'streamlit:set_query_params',
                    queryParams: {{ 'device_id': subscriptionId }}
                }}, '*');
            }}
        }}
      }});
    </script>
    """
    components.html(js_onesignal, height=0, width=0)

    # Captura o ID caso ele já tenha sido gerado
    device_id_capturado = st.query_params.get("device_id", None)

    # FORMULÁRIO DE CADASTRO
    with st.form("form_cliente_direto", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")
        
        # Se já capturamos o ID, mostramos sucesso. Se não, mostramos o botão de ativação
        if device_id_capturado:
            st.success("✅ Seu celular está conectado e pronto para receber os avisos!")
        else:
            st.info("📢 Para se cadastrar, você precisa primeiro ativar as notificações no botão abaixo.")

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

    # BOTÃO EXTRA FORA DO FORMULÁRIO PARA DISPARAR O POP-UP SÓ SE NÃO ESTIVER CADASTRADO
    if not device_id_capturado:
        st.write("---")
        # Injeta um botão HTML/JS que aciona a função de permissão ao ser clicado
        botao_html = """
        <button onclick="window.ativarNotificacoes()" style="
            width: 100%;
            background-color: #FFA500;
            color: white;
            border: none;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        ">👉 Clique Aqui para Ativar Notificações 🔔</button>
        """
        components.html(botao_html, height=50)

    # Lógica de Salvamento
    if botao_cadastrar:
        if nome:
            if not device_id_capturado:
                st.error("⚠️ Erro: Você clicou em se cadastrar, mas ainda não ativou as notificações no botão laranja abaixo!")
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
