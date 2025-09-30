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



# Suponha que seus DataFrames 'combined_df' e 'combined_df_despesas'
# sejam carregados ou criados aqui, como feito anteriormente no notebook.
# Exemplo:
# combined_df = pd.read_excel("planilha_receitas.xlsx", sheet_name='abril') # Substitua pelo seu carregamento real
# combined_df_despesas = pd.read_excel("planilha_despesas.xlsx", sheet_name='abril') # Substitua pelo seu carregamento real

# Função para filtrar dados por mês
def filtrar_dados_por_mes(df, selected_month):
  """
  Filtra o DataFrame combinado por mês.

  Args:
    df: O DataFrame combinado contendo dados de todos os meses.
    selected_month: O mês a ser filtrado (por exemplo, 'abril', 'maio').

  Returns:
    Um DataFrame filtrado para o mês selecionado.
  """
  # Garante que a coluna 'Mês' está em letras minúsculas para filtragem consistente
  df['Mês'] = df['Mês'].str.lower()
  return df[df['Mês'] == selected_month.lower()]


# --- Exemplo de como carregar e combinar seus dados para este script ---
# Substitua esta parte pelo seu código de carregamento de dados real no Streamlit
# Assumindo que você tem os arquivos 'planilha_receitas.xlsx' e 'planilha_despesas.xlsx'
# na mesma pasta do seu script Streamlit no VS Code.

# Carregar as abas de meses para receitas e despesas
excel_file_receitas = pd.ExcelFile("planilha_receitas.xlsx")
excel_file_despesas = pd.ExcelFile("planilha_despesas.xlsx")

months = ['abril', 'maio', 'junho', 'julho', 'agosto']

dfs_receitas = [excel_file_receitas.parse(sheet_name) for sheet_name in months]
dfs_despesas = [excel_file_despesas.parse(sheet_name) for sheet_name in months]

# Combinar os DataFrames de receitas
combined_df = pd.concat(dfs_receitas, ignore_index=True)
combined_df['Mês'] = pd.concat([pd.Series([month] * len(df)) for df, month in zip(dfs_receitas, months)], ignore_index=True)

# Combinar os DataFrames de despesas
combined_df_despesas = pd.concat(dfs_despesas, ignore_index=True)
combined_df_despesas['Mês'] = pd.concat([pd.Series([month] * len(df)) for df, month in zip(dfs_despesas, months)], ignore_index=True)

# --- Fim do exemplo de carregamento de dados ---


# Título da aplicação Streamlit
st.title('Análise Financeira Mensal')

# Lista de meses disponíveis para o filtro
# Certifique-se de que esta lista corresponda aos meses nos seus dados
available_months = combined_df['Mês'].unique().tolist()
available_months.sort() # Opcional: Classificar para melhor visualização

# Cria o seletor de mês na barra lateral
selected_month = st.sidebar.selectbox('Selecione o Mês', available_months)

# Filtra os dados com base no mês selecionado
filtered_revenue_df = filtrar_dados_por_mes(combined_df, selected_month)
filtered_expenses_df = filtrar_dados_por_mes(combined_df_despesas, selected_month)

# Exibe os dados filtrados
st.header(f"Dados de {selected_month.capitalize()}")

st.subheader("Receitas")
st.dataframe(filtered_revenue_df)

st.subheader("Despesas")
st.dataframe(filtered_expenses_df)

# Você pode adicionar seus gráficos e outras análises aqui, usando filtered_revenue_df e filtered_expenses_df
# Exemplo:
# receita_total_mes = filtered_revenue_df['Valor total recebido da parcela (R$)'].sum()
# st.write(f"Receita Total do Mês: R$ {receita_total_mes:.2f}")
