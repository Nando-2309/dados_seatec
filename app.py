import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib as plt
import seaborn as sns
import openpyxl as pxl
import kaleido as k


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Dados Seatec",
    page_icon="📊",
    layout="wide",
)

# --- Carregar dados ---
file_path = "todos_resultados_seatec.xlsx"

df_receitas = pd.read_excel(file_path, sheet_name="Receitas Combinadas")
df_despesas = pd.read_excel(file_path, sheet_name="Despesas Combinadas")
df_faturamento = pd.read_excel(file_path, sheet_name="Faturamento Mensal")
df_ticket = pd.read_excel(file_path, sheet_name="Ticket Medio Mensal Resumo")
df_cancelamentos = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
df_churn = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")

# --- Verificar e limpar os nomes das colunas
df_receitas.columns = df_receitas.columns.str.strip()
df_despesas.columns = df_despesas.columns.str.strip()
df_faturamento.columns = df_faturamento.columns.str.strip()
df_ticket.columns = df_ticket.columns.str.strip()
df_cancelamentos.columns = df_cancelamentos.columns.str.strip()
df_churn.columns = df_churn.columns.str.strip()

# --- Preparar dados ---
df_receitas["Tipo"] = "Receita"
df_despesas["Tipo"] = "Despesa"
df = pd.concat([df_receitas, df_despesas])

# Verificar os nomes das colunas para garantir que 'Categoria' está presente
st.write(df.columns)

df["Data de competência"] = pd.to_datetime(df["Data de competência"], errors="coerce")

# Nova coluna "MesNome" formatada com o nome do mês
df["MesNome"] = df["Data de competência"].dt.strftime("%B %Y")  # Ex: 'Março 2025'

# --- Sidebar (Filtros) ---
st.sidebar.header("Filtros")

# Verificar se a coluna 'Categoria' existe antes de tentar acessá-la
if 'Categoria' in df.columns:
    categorias = df["Categoria"].dropna().unique()
    categorias_sel = st.sidebar.multiselect(
        "Selecione categorias:", categorias, default=categorias
    )
else:
    st.error("A coluna 'Categoria' não foi encontrada no DataFrame!")

# --- Aplicar filtros ---
df_filtrado = df[(df["MesNome"] == mes) & (df["Categoria"].isin(categorias_sel))]

# --- Página Principal ---
st.title("📊 Dashboard Financeiro")

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
(df_receitas.groupby("Mes")["Valor"].sum() - df_despesas.groupby("Mes")["Valor"].sum()).plot(
    kind="line", marker="o", ax=ax4
)
st.pyplot(fig4)

## Gráfico 5 - Churn Rate
st.subheader("Churn Rate")
fig5, ax5 = plt.subplots()
df_churn.plot(x="Mes", y="ChurnRate", kind="line", marker="o", ax=ax5)
st.pyplot(fig5)

## Gráfico 6 - Cancelamentos mês a mês
st.subheader("Cancelamentos")
fig6, ax6 = plt.subplots()
df_cancelamentos.plot(x="Mes", y="Cancelamentos", kind="bar", ax=ax6)
st.pyplot(fig6)

# --- Rodapé (Dados Detalhados) ---
st.subheader("📑 Dados Detalhados")
st.dataframe(df_filtrado)
