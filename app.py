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


# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.github.com/Nando-2309/dados_seatec/blob/main/todos_resultados_seatec.xlsx")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de mês
# Lista de meses para o selectbox
# Certifique-se de que os meses correspondem aos valores na coluna 'Mês' dos seus DataFrames combinados
available_months = combined_df['Mês'].unique().tolist()
available_months.sort() # Opcional: Classificar os meses em ordem alfabética

# Cria um selectbox para o usuário escolher um mês
selected_month = st.selectbox('Selecione o Mês', available_months)

# Filtra os dados com base no mês selecionado
# Assumindo que você tem uma função chamada filter_data_by_month como definida anteriormente
filtered_revenue_df = filter_data_by_month(combined_df, selected_month)
filtered_expenses_df = filter_data_by_month(combined_df_despesas, selected_month)

# Exibe os dados filtrados (você pode substituir isso pelas suas visualizações)
st.write(f"Dados de Receita para {selected_month.capitalize()}:")
st.dataframe(filtered_revenue_df)

st.write(f"Dados de Despesa para {selected_month.capitalize()}:")
st.dataframe(filtered_expenses_df)
