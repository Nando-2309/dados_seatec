import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl as pxl

# --- Carregar dados ---
file_path = "todos_resultados_seatec.xlsx"

df_receitas = pd.read_excel(file_path, sheet_name="Receitas Combinadas")
df_despesas = pd.read_excel(file_path, sheet_name="Despesas Combinadas")
df_faturamento = pd.read_excel(file_path, sheet_name="Faturamento Mensal")
df_ticket = pd.read_excel(file_path, sheet_name="Ticket Medio Mensal Resumo")
df_cancelamentos = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
df_churn = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")

# --- Preparar dados ---
df_receitas["Tipo"] = "Receita"
df_despesas["Tipo"] = "Despesa"
df = pd.concat([df_receitas, df_despesas])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["MesNum"] = df["Data"].dt.month
df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")

# Mapeamento meses por extenso
meses_extenso = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
df["MesNome"] = df["MesNum"].map(meses_extenso)

# --- Sidebar com filtro de mês (com lupa) ---
st.sidebar.header("Filtros")
pesquisa_mes = st.sidebar.text_input("🔍 Pesquisar mês:")
meses_disponiveis = sorted(df["MesNome"].dropna().unique())

# Aplicar filtro de pesquisa
if pesquisa_mes:
    meses_filtrados = [m for m in meses_disponiveis if pesquisa_mes.lower() in m.lower()]
else:
    meses_filtrados = meses_disponiveis

mes_selecionado = st.sidebar.selectbox("Selecione o mês:", meses_filtrados)

# Filtrar dados
df_filtrado = df[df["MesNome"] == mes_selecionado]

# --- Página principal ---
st.title("📊 Dados da Seatec")

## Gráfico 1 - Faturamento Bruto
st.subheader("Faturamento Bruto")
fig1 = px.bar(df_faturamento, x="Mes", y="Faturamento", title="Faturamento Bruto")
st.plotly_chart(fig1, use_container_width=True)

## Gráfico 2 - Ticket Médio
st.subheader("Ticket Médio")
fig2 = px.line(df_ticket, x="Mes", y="TicketMedio", markers=True, title="Ticket Médio")
st.plotly_chart(fig2, use_container_width=True)

## Gráfico 3 - Receitas vs Despesas
st.subheader("Receitas vs Despesas")
df_agg = df_filtrado.groupby("Tipo")["Valor"].sum().reset_index()
fig3 = px.bar(df_agg, x="Tipo", y="Valor", color="Tipo", title="Receitas vs Despesas")
st.plotly_chart(fig3, use_container_width=True)

## Gráfico 4 - Lucratividade Mensal
st.subheader("Lucratividade Mensal")
lucro = df_receitas.groupby("MesNome")["Valor"].sum() - df_despesas.groupby("MesNome")["Valor"].sum()
lucro = lucro.reset_index().rename(columns={0: "Lucro"})
fig4 = px.line(lucro, x="MesNome", y="Valor", markers=True, title="Lucratividade Mensal")
st.plotly_chart(fig4, use_container_width=True)

## Gráfico 5 - Churn Rate
st.subheader("Churn Rate")
fig5 = px.line(df_churn, x="Mes", y="ChurnRate", markers=True, title="Churn Rate")
st.plotly_chart(fig5, use_container_width=True)

## Gráfico 6 - Cancelamentos
st.subheader("Cancelamentos")
fig6 = px.bar(df_cancelamentos, x="Mes", y="Cancelamentos", title="Cancelamentos")
st.plotly_chart(fig6, use_container_width=True)

# --- Rodapé com dados detalhados ---
st.subheader("📑 Dados Detalhados")
st.dataframe(df_filtrado)
