import streamlit as st
import streamlit.components.v1 as components

# ==========================================================================
#  1- LANDING PAGE DE CADASTRO DO CLIENTE (VERSÃO BANNER + OPT-IN CONSENT)
# ==========================================================================

def exibir_cadastro(salvar_cliente_fn):
    # Banner bonito e moderno simulando a identidade visual da padaria artesanal
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

    # JavaScript Otimizado: Só pede permissão quando a função for chamada pelo clique do Checkbox
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
        
        // Função gatilho disparada ao clicar no checkbox do termos
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

    # FORMULÁRIO DE CADASTRO LIMPO E CONFIGURADO
    with st.form("form_cliente_direto", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")
        whatsapp = st.text_input("Seu WhatsApp (com DDD):", placeholder="Ex: 11999998888")

        # Mantendo os seletores caso queira segmentar por produto/horário
        produto = st.selectbox(
            "Qual fornada quer acompanhar?",
            ["🥖 Pão Francês", "🧀 Pão de Queijo", "🥐 Croissant"]
        )

        turno = st.selectbox(
            "Qual horário você costuma vir à padaria?",
            ["Manhã", "Tarde", "Ambos"]
        )

        st.write("") # Espaçador técnico
        
        # A CAIXINHA DE TERMOS (OPT-IN)
        # Como o Streamlit recarrega o form inteiro no submit, usamos um truque visual:
        # Informamos ao cliente para marcar a caixa para liberar o recebimento.
        concordou_termos = st.checkbox(
            "Li e concordo com os termos de uso e aceito receber notificações de fornadas no meu dispositivo.",
            value=True if device_id_capturado else False
        )

        # Status dinâmico de conexão para o cliente ver dentro do form
        if device_id_capturado:
            st.success("✅ Aparelho autorizado com sucesso!")
        else:
            st.warning("🔔 Marque o termo acima e permita o aviso na tela para ativar.")

        st.write("") 
        botao_cadastrar = st.form_submit_button("Me Avise Quando Sair! 🔔", use_container_width=True)

    # Injeção Invisível de JavaScript para monitorar o clique no Checkbox do Streamlit
    # No momento em que o cliente interagir com a tela para marcar os termos, o pop-up pula!
    if not device_id_capturado:
        js_trigger_click = """
        <script>
        setTimeout(() => {
            // Procura a caixinha de seleção na tela do Streamlit e atrela o evento do OneSignal a ela
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

    # Lógica de Salvamento e Envio para o Banco (CSV)
    if botao_cadastrar:
        if nome and whatsapp:
            if not concordou_termos or not device_id_capturado:
                st.error("⚠️ Para concluir, você precisa aceitar os termos e clicar em 'Permitir' no pop-up de notificações do seu navegador.")
            else:
                # Filtra e limpa o número digitado
                wpp_limpo = "".join(filter(str.isdigit, whatsapp))
                if len(wpp_limpo) >= 10 and not wpp_limpo.startswith("55"):
                    wpp_limpo = "55" + wpp_limpo

                # Salva no arquivo CSV misturando os dois modelos (Nome, ID da Tela, WhatsApp, Preferência, Turno)
                # Passamos o WhatsApp também para o operador ter os dados completos na tabela de controle!
                salvar_cliente_fn(nome, device_id_capturado, wpp_limpo, produto, turno)
                
                st.balloons()
                st.success(f"🎉 Perfeito, {nome}! Seu celular foi cadastrado. Você receberá o alerta direto na tela!")
        else:
            st.error("⚠️ Por favor, preencha o Nome e o WhatsApp para continuar.")

    # Rodapé discreto para navegação do operador
    st.write("---")
    if st.button("🔐 Painel de Controle (Uso Interno)", use_container_width=True):
        st.query_params["tela"] = "operador"
        st.rerun()
