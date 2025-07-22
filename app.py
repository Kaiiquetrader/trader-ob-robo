
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Robô de Sinais - trader.ob", layout="centered")

st.title("📈 Robô de Sinais Automático")
st.markdown("Receba sinais de **compra e venda** com base em RSI + Médias Móveis (EMA).")

# Função para cálculo dos indicadores
def calcular_indicadores(dados):
    dados["EMA9"] = dados["Close"].ewm(span=9, adjust=False).mean()
    dados["EMA21"] = dados["Close"].ewm(span=21, adjust=False).mean()
    delta = dados["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    dados["RSI"] = 100 - (100 / (1 + rs))
    return dados

# Função principal de dados
def obter_dados(ativo):
    dados = yf.download(ativo, period="30d", interval="1h")
    if not dados.empty:
        dados = calcular_indicadores(dados)
    return dados

# Entrada do usuário
ativo = st.text_input("Digite o código do ativo (ex: PETR4.SA ou EURUSD=X):", "PETR4.SA")

if ativo:
    dados = obter_dados(ativo)

    if dados.empty or len(dados) < 30:
        st.error("❌ Não foi possível carregar os dados do ativo selecionado. Tente outro ativo ou aguarde alguns minutos.")
    else:
        ultimo = dados.iloc[-1]

        st.subheader("📊 Últimos dados")
        st.write(f"**Preço atual:** R$ {ultimo['Close']:.2f}")
        st.write(f"**RSI:** {ultimo['RSI']:.2f}")
        st.write(f"**EMA 9:** {ultimo['EMA9']:.2f} | **EMA 21:** {ultimo['EMA21']:.2f}")

        # Lógica de sinal
        sinal = ""
        if ultimo["RSI"] < 30 and ultimo["EMA9"] > ultimo["EMA21"]:
            sinal = "🔔 SINAL DE COMPRA"
        elif ultimo["RSI"] > 70 and ultimo["EMA9"] < ultimo["EMA21"]:
            sinal = "🔻 SINAL DE VENDA"
        else:
            sinal = "⏳ Aguardando novo sinal..."

        st.subheader("📢 Sinal gerado:")
        st.markdown(f"<h3 style='color:green'>{sinal}</h3>", unsafe_allow_html=True)
