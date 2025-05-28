import streamlit as st
from woocommerce import API
import json


wcapi = API(
    url=st.secrets["woocommerce"]["url"],
    consumer_key=st.secrets["woocommerce"]["consumer_key"],
    consumer_secret=st.secrets["woocommerce"]["consumer_secret"],
    version="wc/v3"
)

st.set_page_config(page_title="Status de Encomendas", page_icon="📦", layout="wide")
st.header("Atualizar Estado de Encomendas")
st.subheader("Woody Parfum")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


id_encomenda = st.text_input("Digite o número da encomenda")

if id_encomenda:
    try:
        resposta = wcapi.get(f"orders/{id_encomenda}")
        if resposta.status_code == 200:
            encomenda = resposta.json()

            st.subheader(f"Encomenda #{id_encomenda}")
            st.markdown(f'''
            **Cliente:** {encomenda['billing']['first_name']} {encomenda['billing']['last_name']}
            **Data de Criação:** {encomenda['date_created']}
            **Estado da Actual:** {encomenda['status']}
            ''')

            estados = [
                "envio-ctt", "completed", "levantar-loja"
            ]
            default_idx = estados.index(encomenda['status']) if encomenda['status'] in estados else 0
            novo_estado = st.selectbox("Selecione o novo estado", estados, index=default_idx)

            if st.button("Atualizar Estado"):
                update_estado = {"status": novo_estado}
                upd_resposta = wcapi.put(f"orders/{id_encomenda}", update_estado)
                if upd_resposta.status_code == 200:
                    st.success(f"Estado da encomenda atualizado para '{novo_estado}' com sucesso")
                else:
                    st.error(f"Falha ao atualizar estado da encomenda: {upd_resposta.status_code} - {upd_resposta.text}")

        else:
            st.error("Encomenda não encontrada. Confirme o número da encomenda e tente novamente")
    except Exception as e:
        st.error(f"Erro na requisição: {e}")
else:
    st.info("Digite o número da encomenda para carregar detalhes")

st.markdown("---")

