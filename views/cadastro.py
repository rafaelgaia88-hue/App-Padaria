import streamlit as st
import streamlit.components.v1 as components

# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (CAMPOS OBRIGATÓRIOS E TRAVA ENTER)
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

    # JavaScript Otimizado para o OneSignal
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
        
        window.dispararPermissaoNotificacao = async function() {{
            try {{
                await OneSignal.Notifications.requestPermission();
                let subscriptionId = OneSignal.User.PushSubscription.id;
                if (subscriptionId) {{
                    window.parent.postMessage({{
                        type: 'streamlit:set_query_params',
                        queryParams: {{ 'device_id': subscriptionId }}
                    }}, '*');
                }}
            }} catch(e) {{
                console.error("Erro ao solicitar permissao:", e);
            }}
        }}
      }});
    </script>
    """
    components.html(js_onesignal, height=0, width=0)

    # Captura o ID do dispositivo retornado pelo JavaScript
    device_id_capturado = st.query_params.get("device_id", None)

    # CORREÇÃO CRÍTICA: Removido 'clear_on_submit=True' para os dados NÃO sumirem se o cliente errar ou apertar Enter
    with st.form("form_cliente_direto", clear_on_submit=False):
        # Campos marcados visualmente com "*" indicando obrigatoriedade
        nome = st.text_input("Seu Nome *:")
        whatsapp = st.text_input("Seu WhatsApp (com DDD) *:", placeholder="Ex: 11999998888")

        produto = st.selectbox(
            "Qual fornada quer acompanhar?",
            ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
        )

        turno = st.selectbox(
            "Qual horário você costuma vir à padaria?",
            ["Manhã", "Tarde", "Ambos"]
        )

        st.write("") 
        
        # Caixinha de Termos (Opt-in)
        concordou_termos = st.checkbox(
            "Li e concordo com os termos de uso e aceito receber notificações de fornadas no meu dispositivo.",
            value=True if device_id_capturado else False
        )

        # Status dinâmico de conexão
        if device_id_capturado:
            st.success("✅ Aparelho autorizado com sucesso!")
        else:
            st.warning("🔔 Marque o termo acima e permita o aviso na tela para ativar.")

        st.write("") 
        botao_cadastrar = st.form_submit_button("Me Avise Quando Sair! 🔔", use_container_width=True)

    # Injeção Invisível de JavaScript para capturar cliques na caixinha de termos
    if not device_id_capturado:
        js_trigger_click = """
        <script>
        setTimeout(() => {
            const checkboxes = window.parent.document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.addEventListener('change', function() {
                    if(this.checked) {
                        window.parent.dispararPermissaoNotificacao();
                    }
                });
            });
        }, 1000);
        </script>
        """
        components.html(js_trigger_click, height=0, width=0)

    # LÓGICA DE VALIDAÇÃO ESTREITA E SALVAMENTO
    if botao_cadastrar:
        # 1. Validação: Impede campos vazios de avançarem
        if not nome.strip() or not whatsapp.strip():
            st.error("⚠️ Erro: Os campos de Nome e WhatsApp são obrigatórios! Preencha-os antes de continuar.")
        
        # 2. Validação: Garante que os termos e o ID da tela estejam ativos
        elif not concordou_termos or not device_id_capturado:
            st.error("⚠️ Para concluir, você precisa aceitar os termos e clicar em 'Permitir' no pop-up de notificações do seu navegador.")
        
        # 3. Tudo correto -> Salva os dados
        else:
            wpp_limpo = "".join(filter(str.isdigit, whatsapp))
            
            # Validação secundária de tamanho de número brasileiro
            if len(wpp_limpo) < 10:
                st.error("⚠️ Por favor, insira um número de WhatsApp válido contendo o DDD.")
            else:
                if not wpp_limpo.startswith("55"):
                    wpp_limpo = "55" + wpp_limpo

                # Salva os dados no banco CSV de forma segura
                salvar_cliente_fn(nome, device_id_capturado, wpp_limpo, produto, turno)
                
                st.balloons()
                st.success(f"🎉 Perfeito, {nome}! Seu celular foi cadastrado. Você receberá o alerta direto na tela!")
                
                # Opcional: Força uma limpeza na tela apenas APÓS o cadastro de sucesso absoluto se desejar, 
                # mas mantendo o padrão do Streamlit para evitar perdas acidentais de digitação.

    # Rodapé discreto para navegação do operador
    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params["tela"] = "operador"
        st.rerun()
