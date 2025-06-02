import streamlit as st
from woocommerce import API
import json

wcapi = API(
    url=st.secrets["woocommerce"]["url"],
    consumer_key=st.secrets["woocommerce"]["consumer_key"],
    consumer_secret=st.secrets["woocommerce"]["consumer_secret"],
    version="wc/v3"
)

st.set_page_config(page_title="APP Estado de Encomendas", page_icon="📦", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


def verificar_credencias(username: str, password: str, utilizadores_secrets: dict) -> bool:
    if username in utilizadores_secrets:
        return utilizadores_secrets[username] == password
    return False

utilizadores_db = st.secrets["utilizadores"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def login_page() -> None:
    st.markdown(
        """
        <style>
            /* Esconde o botão que alterna (abre/fecha) a sidebar */
            button[title="Toggle sidebar"] {
                display: none;
            }
            /* Esconde por completo a própria sidebar */
            [data-testid="stSidebar"] {
                visibility: hidden;
                width: 0px;  /* opcional: reduz a largura a zero */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title(f'Login {st.secrets["dados_cliente"]["nome"]}')

    utilizador = st.text_input("Utilizador", max_chars=50)
    password = st.text_input("Password", type="password", max_chars=50)

    if st.button("Entrar"):
        if verificar_credencias(utilizador, password, utilizadores_db):
            st.session_state.logged_in = True
            st.session_state.username = utilizador
            st.success(f"Bem vindo(a), {utilizador} !")
            st.rerun()
        else:
            st.error("Utilizador ou Password inválidos.")

def home_page() -> None:
    st.markdown(
        """
        <style>
            /* Ao entrar no home_page, voltamos a expor sidebar e toggle */
            button[title="Toggle sidebar"] {
                display: block;
            }
            [data-testid="stSidebar"] {
                visibility: visible;
                width: auto;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.write(st.secrets["dados_cliente"]["nome"])
    st.sidebar.write(f"Utilizador: **{st.session_state.username}**")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.header("Atualizar Estado de Encomendas")
    id_encomenda = st.text_input("Digite o número da encomenda")

    if id_encomenda:
        try:
            resposta = wcapi.get(f"orders/{id_encomenda}")
            if resposta.status_code == 200:
                encomenda = resposta.json()

                st.subheader(f"Encomenda #{id_encomenda}")
                st.markdown(f'''
                **Cliente:** {encomenda['billing']['first_name']} {encomenda['billing']['last_name']}\n
                **Data de Criação:** {encomenda['date_created']}\n
                **Estado da Actual:** {encomenda['status']}
                ''')

                estados = [
                    "envio-ctt", "levantar-loja", "completed", "envio-avaliacao", "finalizada"
                ]
                rotulos = {
                    "envio-ctt": "Enviar para os CTT",
                    "levantar-loja": "Disponível para Levantamento na Loja",
                    "completed": "Entregue ao Cliente",
                    "envio-avaliacao": "Enviar Pedido de Avaliação da Compra",
                    "finalizada": "Avaliação Recebida"
                }
                default_idx = estados.index(encomenda['status']) if encomenda['status'] in estados else 0

                novo_estado = st.selectbox("Selecione o novo estado", estados, index=default_idx,
                                           format_func=lambda code: rotulos.get(code, code))

                if st.button("Atualizar Estado"):
                    update_estado = {"status": novo_estado}
                    upd_resposta = wcapi.put(f"orders/{id_encomenda}", update_estado)
                    if upd_resposta.status_code == 200:
                        st.success(f"Estado da encomenda atualizado para '{novo_estado}' com sucesso")
                    else:
                        st.error(
                            f"Falha ao atualizar estado da encomenda: {upd_resposta.status_code} - {upd_resposta.text}")

            else:
                st.error("Encomenda não encontrada. Confirme o número da encomenda e tente novamente.")
        except Exception as e:
            st.error(f"Erro na requisição: {e}")

    st.markdown("---")



def main() -> None:
    if not st.session_state.logged_in:
        login_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
