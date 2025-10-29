import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIGURAÇÕES INICIAIS
# =============================
st.set_page_config(
    page_title="Dashboard de Vazão",
    layout="wide",
    page_icon="💧"
)

st.title("💧 Dashboard de Vazão do Sensor de Fluxo")
st.markdown("Visualize a vazão em tempo real, somatórios por hora e volume total acumulado.")

# =============================
# LEITURA DOS DADOS
# =============================
uploaded_file = st.file_uploader("📂 Selecione o arquivo 'dados_vazao.xlsx'", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ajustar nomes de colunas, caso venham com espaços extras
    df.columns = [col.strip() for col in df.columns]

    # Converter Timestamp para datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Remover linhas inválidas
    df = df.dropna(subset=["Timestamp"])

    # Ordenar por tempo
    df = df.sort_values(by="Timestamp")

    # Calcular volume em litros (L/s * 1 segundo)
    df["Volume (L)"] = df["Vazão (L/s)"]

    # Agrupar por hora
    df_hora = (
        df.groupby(df["Timestamp"].dt.floor("H"))
        .agg({
            "Pulsos": "sum",
            "Vazão (L/min)": "mean",
            "Vazão (L/s)": "mean",
            "Volume (L)": "sum"
        })
        .reset_index()
        .rename(columns={"Timestamp": "Hora"})
    )

    # =============================
    # MÉTRICAS GERAIS
    # =============================
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Vazão média (L/min)", f"{df['Vazão (L/min)'].mean():.2f}")
    col2.metric("💧 Volume total (L)", f"{df['Volume (L)'].sum():.2f}")
    col3.metric("🕒 Registros totais", len(df))

    st.markdown("---")

    # =============================
    # GRÁFICO 1 – Vazão ao longo do tempo
    # =============================
    st.subheader("📊 Vazão ao longo do tempo (L/s)")

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df["Timestamp"], df["Vazão (L/s)"], marker="o", linestyle="-")
    ax1.set_xlabel("Tempo")
    ax1.set_ylabel("Vazão (L/s)")
    ax1.set_title("Variação da Vazão ao Longo do Tempo")
    st.pyplot(fig1)

    # =============================
    # GRÁFICO 2 – Volume por hora
    # =============================
    st.subheader("📆 Volume acumulado por hora")

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(df_hora["Hora"], df_hora["Volume (L)"], width=0.03)
    ax2.set_xlabel("Hora")
    ax2.set_ylabel("Volume Total (L)")
    ax2.set_title("Volume Total por Hora")
    st.pyplot(fig2)

    # =============================
    # TABELA DE DADOS AGRUPADOS
    # =============================
    st.subheader("📋 Dados agregados por hora")
    st.dataframe(df_hora.style.format({
        "Vazão (L/min)": "{:.2f}",
        "Vazão (L/s)": "{:.4f}",
        "Volume (L)": "{:.2f}"
    }))

else:
    st.info("⬆️ Faça o upload do arquivo 'dados_vazao.xlsx' para visualizar o dashboard.")
