import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib as plt
import seaborn as sns
import openpyxl as pxl
import kaleido as k


# --- Carregar os dados ---
file_path = "todos_resultados_seatec.xlsx"

df_receitas = pd.read_excel(file_path, sheet_name="Receitas Combinadas")
df_despesas = pd.read_excel(file_path, sheet_name="Despesas Combinadas")
df_faturamento = pd.read_excel(file_path, sheet_name="Faturamento Mensal")
df_ticket = pd.read_excel(file_path, sheet_name="Ticket Medio Mensal Resumo")
df_cancelamentos = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
df_churn = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")

# --- Preparar dados de receitas e despesas ---
df_receitas["Tipo"] = "Receita"
df_despesas["Tipo"] = "Despesa"
df = pd.concat([df_receitas, df_despesas])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["MesNum"] = df["Data"].dt.month
df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")

# Dicionário para traduzir número do mês -> nome por extenso
meses_extenso = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# --- Sidebar com filtro de mês ---
st.sidebar.header("Filtros")
meses_disponiveis = sorted(df["MesNum"].dropna().unique())
mes_selecionado = st.sidebar.selectbox(
    "Selecione o mês:",
    [meses_extenso[m] for m in meses_disponiveis]
)

# Converter escolha para número
mes_num = {v: k for k, v in meses_extenso.items()}[mes_selecionado]

# Filtrar dados
df_filtrado = df[df["MesNum"] == mes_num]

# --- Página principal ---
st.title("📊 Dados da Seatec")

## Gráfico 1 - Faturamento Bruto
st.subheader("Faturamento Bruto")
fig1, ax1 = plt.subplots()
df_faturamento.plot(x="Mes", y="Faturamento", kind="bar", ax=ax1)
st.pyplot(fig1)

## Gráfico 2 - Ticket Médio
st.subheader("Ticket Médio")
fig2, ax2 = plt.subplots()
df_ticket.plot(x="Mes", y="TicketMedio", kind="line", marker="o", ax=ax2)
st.pyplot(fig2)

## Gráfico 3 - Receitas vs Despesas
st.subheader("Receitas vs Despesas")
fig3, ax3 = plt.subplots()
df_filtrado.groupby("Tipo")["Valor"].sum().plot(kind="bar", ax=ax3)
st.pyplot(fig3)

## Gráfico 4 - Lucratividade Mensal
st.subheader("Lucratividade Mensal")
fig4, ax4 = plt.subplots()
(df_receitas.groupby("MesNum")["Valor"].sum() - df_despesas.groupby("MesNum")["Valor"].sum()).plot(
    kind="line", marker="o", ax=ax4
)
st.pyplot(fig4)

## Gráfico 5 - Churn Rate
st.subheader("Churn Rate")
fig5, ax5 = plt.subplots()
df_churn.plot(x="Mes", y="ChurnRate", kind="line", marker="o", ax=ax5)
st.pyplot(fig5)

## Gráfico 6 - Cancelamentos
st.subheader("Cancelamentos")
fig6, ax6 = plt.subplots()
df_cancelamentos.plot(x="Mes", y="Cancelamentos", kind="bar", ax=ax6)
st.pyplot(fig6)

# --- Rodapé com dados detalhados ---
st.subheader("📑 Dados Detalhados")
st.dataframe(df_filtrado)