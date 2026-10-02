import streamlit as st
import streamlit.components.v1 as components

def exibir_cadastro(salvar_cliente_fn):
    st.markdown(
        """
        <div style='text-align: center; background-color: #1E1E1E; padding: 25px; border-radius: 12px; border: 1px solid #FFA500; margin-bottom: 20px;'>
            <span style='font-size: 3.5rem;'>🥖</span>
            <h1 style='font-size: 2.2rem; color: #FFF; margin: 10px 0 0 0; font-family: sans-serif;'>Seja Bem-Vindo!</h1>
            <p style='font-size: 1.2rem; color: #FFA500; font-weight: bold; margin: 5px 0 0 0;'>Padaria Doce Sabor</p>
            <p style='font-size: 0.95rem; color: #AAA; margin: 10px 0 0 0; line-height: 1.4;'>
                Inscreva-se para receber um aviso instantâneo direto na sua tela assim que o pãozinho sair quentinho do forno!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ONESIGNAL_APP_ID = "f41c3cb4-bef4-4144-9a2b-9f823fd5fe4d"

    js_onesignal = f"""
    <script src="https://onesignal.com" async></script>
    <script>
      window.OneSignal = window.OneSignal || [];
      OneSignal.push(async function() {{
        await OneSignal.init({{
          appId: "{ONESIGNAL_APP_ID}",
          allowLocalhostAsSecureOrigin: true
        }});
        
        window.dispararPrompt = async function() {{
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
    device_id_capturado = st.query_params.get("device_id", None)

    with st.form("form_cliente_direto", clear_on_submit=False):
        nome = st.text_input("Seu Nome *:")
        whatsapp = st.text_input("Seu WhatsApp (com DDD) *:", placeholder="Ex: 11999998888")

        produto = st.selectbox("Qual fornada quer acompanhar?", ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"])
        turno = st.selectbox("Qual horário você costuma vir à padaria?", ["Manhã", "Tarde", "Ambos"])

        st.write("") 
        concordou_termos = st.checkbox("Li e concordo com os termos de uso.")

        # SE O APARELHO FOR RECONHECIDO, MOSTRA SUCESSO. SE NÃO, MOSTRA O BOTÃO BONITO DE ATIVAÇÃO
        if device_id_capturado:
            st.success("✅ Seu dispositivo está conectado com sucesso!")
        else:
            # Botão HTML elegante embutido no layout do formulário
            botao_ativar_html = """
            <div style='text-align: center; margin: 10px 0;'>
                <button type='button' onclick='window.parent.dispararPrompt()' style='width: 100%; background-color: #FFA500; color: white; border: none; padding: 10px; font-weight: bold; border-radius: 6px; cursor: pointer;'>
                    🔔 CLIQUE AQUI PARA ATIVAR NOTIFICAÇÕES
                </button>
            </div>
            """
            components.html(botao_ativar_html, height=50)

        st.write("") 
        botao_cadastrar = st.form_submit_button("Me Avise Quando Sair! 🔔", use_container_width=True)

    if botao_cadastrar:
        if not nome.strip() or not whatsapp.strip():
            st.error("⚠️ Os campos de Nome e WhatsApp são obrigatórios.")
        elif not concordou_termos:
            st.error("⚠️ Você precisa aceitar os termos de uso.")
        elif not device_id_capturado:
            st.error("⚠️ Ative as notificações no botão laranja acima antes de finalizar o seu cadastro!")
        else:
            wpp_limpo = "".join(filter(str.isdigit, whatsapp))
            if len(wpp_limpo) >= 10:
                if not wpp_limpo.startswith("55"):
                    wpp_limpo = "55" + wpp_limpo
                salvar_cliente_fn(nome, device_id_capturado, wpp_limpo, produto, turno)
                st.balloons()
                st.success(f"🎉 Perfeito, {nome}! Cadastro concluído com sucesso!")

    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params["tela"] = "operador"
        st.rerun()
