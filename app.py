import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Importar plotly.graph_objects para o gráfico de faturamento

# --- Configuração da página ---
st.set_page_config(layout="wide")

# --- Carregar dados ---
# Substitua pelo caminho correto do seu arquivo Excel
file_path = "todos_resultados_seatec.xlsx"

try:
    df_receitas_combinadas = pd.read_excel(file_path, sheet_name="Receitas Combinadas")
    df_despesas_combinadas = pd.read_excel(file_path, sheet_name="Despesas Combinadas")
    df_faturamento_mensal = pd.read_excel(file_path, sheet_name="Faturamento Mensal")
    # Load other sheets as needed for your calculations and visualizations
    df_cancelamentos_resumo = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
    df_churn_rate_resumo = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")
    df_clientes_cancelados_detalhe = pd.read_excel(file_path, sheet_name="Clientes Cancelados Detalhe") # Carregar detalhes dos cancelados
    df_receita_mensal_resumo = pd.read_excel(file_path, sheet_name="Receita Mensal Resumo") # Load Receita Mensal Resumo


except FileNotFoundError:
    st.error(f"Erro: O arquivo {file_path} não foi encontrado. Certifique-se de que o arquivo está no diretório correto.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo Excel: {e}")
    st.stop()


# --- Preparar dados ---
# Adicionar coluna 'Tipo' aos DataFrames de receitas e despesas antes de concatenar
df_receitas_combinadas["Tipo"] = "Receita"
df_despesas_combinadas["Tipo"] = "Despesa"

# Concatenar receitas e despesas para o filtro de mês
df_combined = pd.concat([df_receitas_combinadas, df_despesas_combinadas], ignore_index=True)


# Mapeamento meses por extenso para ordenação
month_order = ['abril', 'maio', 'junho', 'julho', 'agosto'] # Ajuste conforme seus dados
meses_extenso = {
    'abril': 'Abril', 'maio': 'Maio', 'junho': 'Junho',
    'julho': 'Julho', 'agosto': 'Agosto'
}

# Garantir que a coluna 'Mês' esteja presente e usar o mapeamento
if 'Mês' in df_combined.columns:
    df_combined['Mês Nome Extenso'] = df_combined['Mês'].map(meses_extenso)
else:
    st.error("Coluna 'Mês' não encontrada no DataFrame combinado.")
    st.stop()

# Converter a coluna 'Mês' nos DataFrames resumo para categoria com ordem
for df_resumo in [df_faturamento_mensal, df_cancelamentos_resumo, df_churn_rate_resumo, df_receita_mensal_resumo]: # Added df_receita_mensal_resumo
    if 'Mês' in df_resumo.columns:
        df_resumo['Mês'] = pd.Categorical(df_resumo['Mês'], categories=[meses_extenso[m] for m in month_order], ordered=True)
        df_resumo = df_resumo.sort_values('Mês') # Ordenar pelo mês
    else:
         st.warning(f"Coluna 'Mês' não encontrada no DataFrame resumo: {df_resumo}")


# Re-calculate ticket medio inside the Streamlit app using the original logic
# Filter the combined DataFrame to include only monthly fees (TC and S8) in any Category column
mensalidades_df = df_combined[
    (df_combined['Categoria 1'].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE'])) |
    (df_combined['Categoria 2'].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE'])) |
    (df_combined['Categoria 3'].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE'])) |
    (df_combined['Categoria 4'].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE'])) |
    (df_combined['Categoria 5'].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE']))
].copy() # Adicionado .copy() para evitar SettingWithCopyWarning

# Create a new column with the total monthly fee per row
# Initialize the column with 0
mensalidades_df['Valor Total Mensalidade'] = 0.0

# Sum the monthly fee values in each Category column where the category matches
for i in range(1, 6):
    categoria_col = f'Categoria {i}'
    valor_col = f'Valor na Categoria {i}'
    # Use .loc to avoid SettingWithCopyWarning
    mensalidades_df.loc[mensalidades_df[categoria_col].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE']), 'Valor Total Mensalidade'] += \
        mensalidades_df.loc[mensalidades_df[categoria_col].isin(['MENSALIDADE TC', 'MENSALIDADE S8','MENSALIDADE TC - PRO RATA OU PGTO. FINAL', 'MENSALIDADE S8 - PRO RATA OU PGTO. FINAL', 'MENSALIDADE SITE', 'CONTRATO DE MANUTENÇÃO HARDWARE']), valor_col].fillna(0)

# Calculate the monthly average ticket using the new 'Valor Total Mensalidade' column
# Group the filtered DataFrame by month and calculate the mean of the new column
ticket_medio_mensalidades = mensalidades_df.groupby('Mês')['Valor Total Mensalidade'].mean().reset_index() # Reset index to make 'Mês' a column

# Ensure the 'Mês' column in ticket_medio_mensalidades is in categorical format with the correct order and mapped to full names
ticket_medio_mensalidades['Mês Nome Extenso'] = ticket_medio_mensalidades['Mês'].map(meses_extenso)
ticket_medio_mensalidades['Mês Nome Extenso'] = pd.Categorical(ticket_medio_mensalidades['Mês Nome Extenso'], categories=[meses_extenso[m] for m in month_order], ordered=True)
ticket_medio_mensalidades = ticket_medio_mensalidades.sort_values('Mês Nome Extenso') # Sort by full month name


# --- Sidebar com filtro de mês ---
st.sidebar.header("🔍 Filtros") # Adicionado ícone de lupa

# Obter meses disponíveis do DataFrame combinado e usar os nomes por extenso para o filtro
meses_disponiveis_extenso = [meses_extenso[m] for m in month_order if m in df_combined['Mês'].unique()]

# Multi-select para meses com todos selecionados por padrão
meses_selecionados_extenso = st.sidebar.multiselect("Selecione o(s) mês(es):", meses_disponiveis_extenso, default=meses_disponiveis_extenso)

# Mapear os meses selecionados de volta para o formato original (abril, maio, etc.) para filtrar
meses_selecionados_original = [k for k, v in meses_extenso.items() if v in meses_selecionados_extenso]

# Filtrar dados combinados pelos meses selecionados
df_filtrado = df_combined[df_combined["Mês"].isin(meses_selecionados_original)].copy() # Usar .copy() para evitar SettingWithCopyWarning


# --- Página principal ---
st.title("📊 Dados da Seatec")

## Gráfico 1 - Faturamento Bruto (usando df_faturamento_mensal ordenado)
st.subheader("Faturamento Bruto")

fig1 = px.bar(
    df_faturamento_mensal,
    x="Valor_Receita",  # <- Confirme se no Excel está escrito exatamente assim
    y="Mês",
    orientation='h',
    title="Faturamento Bruto Mensal",
    color="Mês"
)
st.plotly_chart(fig1, use_container_width=True)

## Gráfico 2 - Ticket Médio (usando ticket_medio_mensalidades calculado in-app)
st.subheader("Ticket Médio Mensal")

# Check if the DataFrame is not empty before plotting
if not ticket_medio_mensalidades.empty:
    # Create a line chart using go.Scatter
    fig2 = go.Figure(data=go.Scatter(x=ticket_medio_mensalidades['Mês Nome Extenso'], y=ticket_medio_mensalidades['Valor Total Mensalidade'], mode='lines+markers'))

    # Update layout for the line chart
    fig2.update_layout(
        title='Ticket Médio Mensal',
        xaxis_title='Mês',
        yaxis_title='Ticket Médio (R$)'
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Dados de ticket médio não disponíveis para os meses selecionados.")


# --- Gráfico 3: Receitas vs Despesas ---
st.subheader("Receitas vs Despesas")

# Criar dataframe de meses (garante ordem correta)
df_meses = pd.DataFrame({
    "Mês Nome Extenso": [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
})

# --- Agrupar Receitas ---
df_receitas_agg =  df_receitas_combinadas.groupby("Mês Nome Extenso", as_index=False)["Valor Pago"].sum()
df_receitas_agg.rename(columns={"Valor Pago": "Valor_Receita"}, inplace=True)

# --- Agrupar Despesas ---
df_despesas_agg = df_despesas_combinadas.groupby("Mês Nome Extenso", as_index=False)["Valor total pago da parcela (R$)"].sum()
df_despesas_agg.rename(columns={"Valor total pago da parcela (R$)": "Valor_Despesa"}, inplace=True)

# Ajustar despesas para valores positivos (caso venham negativos)
df_despesas_agg["Valor_Despesa"] = df_despesas_agg["Valor_Despesa"].abs()

# --- Juntar Receitas + Despesas com todos os meses ---
df_agrupado = df_meses.merge(df_receitas_agg, on="Mês Nome Extenso", how="left")
df_agrupado = df_agrupado.merge(df_despesas_agg, on="Mês Nome Extenso", how="left")
df_agrupado.fillna(0, inplace=True)

# Garantir ordem dos meses
df_agrupado["Mês Nome Extenso"] = pd.Categorical(
    df_agrupado["Mês Nome Extenso"],
    categories=df_meses["Mês Nome Extenso"],
    ordered=True
)

# --- Transformar em formato longo (para barras lado a lado) ---
df_long = df_agrupado.melt(
    id_vars="Mês Nome Extenso",
    value_vars=["Valor_Receita", "Valor_Despesa"],
    var_name="Tipo",
    value_name="Valor"
)

# Ajustar labels
df_long["Tipo"] = df_long["Tipo"].replace({
    "Valor_Receita": "Receita",
    "Valor_Despesa": "Despesa"
})

# --- Criar gráfico ---
fig = px.bar(
    df_long,
    x="Mês Nome Extenso",
    y="Valor",
    color="Tipo",
    barmode="group",
    title="Receitas vs Despesas por Mês"
)

st.plotly_chart(fig, use_container_width=True)


## Gráfico 4 - Lucratividade Mensal (usando df_faturamento_mensal ordenado)
st.subheader("Lucratividade Mensal")
# Criando o gráfico de barras e linha sobreposta usando Plotly Go
# Usar o df_faturamento_mensal que já está ordenado por Mês (feito na preparação dos dados)
if not df_faturamento_mensal.empty:
    fig4 = go.Figure(data=[
        go.Bar(name='Faturamento', x=df_faturamento_mensal['Mês'], y=df_faturamento_mensal['Faturamento'], marker_color='blue'),
        go.Scatter(name='Evolução da Lucratividade', x=df_faturamento_mensal['Mês'], y=df_faturamento_mensal['Faturamento'], mode='lines+markers', line=dict(color='purple', width=4), marker=dict(color='purple', size=6))
    ])

    # Atualizando o layout
    fig4.update_layout(
        title='Lucratividade Mensal (R$)',
        xaxis_title='Mês',
        yaxis_title='Faturamento (R$)',
        xaxis_tickangle=45,
        barmode='overlay' # Para sobrepor a linha nas barras
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("Dados de faturamento mensal não disponíveis.")


## Gráfico 5 - Churn Rate (usando df_churn_rate_resumo ordenado)
st.subheader("Taxa de Rotatividade (Churn Rate) Mensal")
# Adicionado gráfico de pizza para Churn Rate
# O nome da coluna no excel sheet "Churn Rate Resumo" para os valores é 'Identificador do cliente'
if not df_churn_rate_resumo.empty:
    fig5 = px.pie(df_churn_rate_resumo, values='Identificador do cliente', names='Mês',
             title='Taxa de Rotatividade (Churn Rate) por Mês')

    # Atualiza os traços para mostrar o percentual real de churn rate para cada mês
    # Precisamos formatar os valores de churn rate como strings com '%'
    # Certifique-se que a coluna de valores no df_churn_rate_resumo é a correta para o cálculo do percentual na pizza
    # Assumindo que 'Identificador do cliente' no df_churn_rate_resumo representa o valor para o cálculo do percentual
    # Verifique se a soma dos valores é maior que zero para evitar divisão por zero
    total_churn = df_churn_rate_resumo['Identificador do cliente'].sum()
    if total_churn > 0:
        # Calculate percentages based on the values in the DataFrame
        churn_rate_percentages = [f'{(val / total_churn):.1%}' for val in df_churn_rate_resumo['Identificador do cliente'].values]
        fig5.update_traces(textinfo='percent+label', insidetextorientation='radial', text=churn_rate_percentages) # Use percent+label to show both
    else:
         fig5.update_traces(textinfo='label+value', insidetextorientation='radial') # Show only label and value if total is zero or null


    # Update layout to change the title font size and make it bold
    fig5.update_layout(
        title={
            'text': 'Taxa de Rotatividade (Churn Rate) por Mês',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'size': 20,
                'family': 'Arial',
                'color': 'black',
                'weight': 'bold' # Make title bold
            }
        }
    )
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("Dados de Churn Rate não disponíveis.")


## Gráfico 6 - Cancelamentos (usando df_clientes_cancelados_detalhe e df_cancelamentos_resumo)
st.subheader("Cancelamentos Mês a Mês")
# Added boxplot for Cancellations
# Use df_clientes_cancelados_detalhe for the boxplot, which contains the individual values per cancellation
# Map the original month to the full name for the X axis
if 'Mês' in df_clientes_cancelados_detalhe.columns:
    df_clientes_cancelados_detalhe['Mês Nome Extenso'] = df_clientes_cancelados_detalhe['Mês'].map(meses_extenso)

    # Create the boxplot using Plotly Express
    # Ensure that the 'Valor total recebido da parcela (R$)' column exists in this DataFrame
    if 'Valor total recebido da parcela (R$)' in df_clientes_cancelados_detalhe.columns and not df_clientes_cancelados_detalhe.empty:
        fig6 = px.box(df_clientes_cancelados_detalhe, x='Mês Nome Extenso', y='Valor total recebido da parcela (R$)',
                  title='Cancelamentos Mês a Mês - Distribuição de Valores',
                  category_orders={'Mês Nome Extenso': [meses_extenso[m] for m in month_order]}) # Order the months

        st.plotly_chart(fig6, use_container_width=True)
    elif df_clientes_cancelados_detalhe.empty:
        st.warning("Dados de clientes cancelados não disponíveis para o boxplot.")
    else:
        st.warning("Coluna 'Valor total recebido da parcela (R$)' não encontrada no DataFrame de detalhes dos clientes cancelados para o boxplot.")
else:
    st.warning("Coluna 'Mês' não encontrada no DataFrame de detalhes dos clientes cancelados para o boxplot.")



# --- Rodapé com dados detalhados ---
st.subheader(f"📑 Dados Detalhados dos Meses Selecionados")

# Exibir apenas as colunas relevantes e renomeá-las para melhor visualização, se necessário
colunas_detalhes = ['Identificador do cliente', 'Nome do cliente', 'Descrição', 'Valor total recebido da parcela (R$)', 'Categoria 1', 'Valor na Categoria 1', 'Mês Nome Extenso'] # Exemplo

# Check if df_filtrado is not empty before selecting columns
if not df_filtrado.empty:
    # Ensure all required columns exist in df_filtrado before selecting
    required_cols_detalhes = [col for col in colunas_detalhes if col in df_filtrado.columns]
    df_detalhes_filtrado = df_filtrado[required_cols_detalhes].copy()

    # Opcional: Renomear colunas para português
    df_detalhes_filtrado.rename(columns={
        'Identificador do cliente': 'ID Cliente',
        'Nome do cliente': 'Nome Cliente',
        'Descrição': 'Descrição',
        'Valor total recebido da parcela (R$)': 'Valor Recebido Total (R$)',
        'Categoria 1': 'Categoria Principal',
        'Valor na Categoria 1': 'Valor Categoria Principal (R$)',
        'Mês Nome Extenso': 'Mês'
    }, inplace=True)


    st.dataframe(df_detalhes_filtrado)
else:
    st.warning("Dados detalhados não disponíveis para os meses selecionados.")


# Exibir detalhes dos clientes cancelados para os meses selecionados
st.subheader(f"❌ Detalhes dos Clientes Cancelados nos Meses Selecionados")

# Filtrar o DataFrame de detalhes dos cancelados pelos meses selecionados
# Check if df_clientes_cancelados_detalhe is not empty before filtering
if not df_clientes_cancelados_detalhe.empty:
    df_cancelados_mes = df_clientes_cancelados_detalhe[df_clientes_cancelados_detalhe['Mês'].isin(meses_selecionados_original)].copy()

    # Exibir as colunas relevantes para os detalhes dos cancelados
    colunas_cancelados = ['Identificador do cliente', 'Nome do cliente', 'Descrição', 'Valor total recebido da parcela (R$)', 'Mês Nome Extenso'] # Incluir Mês Nome Extenso
    # Ensure all required columns exist in df_cancelados_mes before selecting
    required_cols_cancelados = [col for col in colunas_cancelados if col in df_cancelados_mes.columns]
    df_cancelados_mes_detalhes = df_cancelados_mes[required_cols_cancelados].copy()


    # Opcional: Renomear colunas para português
    df_cancelados_mes_detalhes.rename(columns={
        'Identificador do cliente': 'ID Cliente',
        'Nome do cliente': 'Nome Cliente',
        'Descrição': 'Descrição',
        'Valor total recebido da parcela (R$)': 'Valor Recebido (R$)',
        'Mês Nome Extenso': 'Mês'
    }, inplace=True)

    st.dataframe(df_cancelados_mes_detalhes)
else:
    st.warning("Detalhes de clientes cancelados não disponíveis para os meses selecionados.")