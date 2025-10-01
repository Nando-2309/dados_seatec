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
    df_ticket_medio_mensal = pd.read_excel(file_path, sheet_name="Ticket Medio Mensal Resumo")
    df_cancelamentos_resumo = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
    df_churn_rate_resumo = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")
    df_clientes_cancelados_detalhe = pd.read_excel(file_path, sheet_name="Clientes Cancelados Detalhe") # Carregar detalhes dos cancelados

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
for df_resumo in [df_faturamento_mensal, df_ticket_medio_mensal, df_cancelamentos_resumo, df_churn_rate_resumo]:
    if 'Mês' in df_resumo.columns:
        df_resumo['Mês'] = pd.Categorical(df_resumo['Mês'], categories=[meses_extenso[m] for m in month_order], ordered=True)
        df_resumo = df_resumo.sort_values('Mês') # Ordenar pelo mês
    else:
         st.warning(f"Coluna 'Mês' não encontrada no DataFrame resumo: {df_resumo}")


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
# Modificado para gráfico de barras horizontal e colorido
fig1 = px.bar(df_faturamento_mensal, x="Valor_Receita", y="Mês", orientation='h',
              title="Faturamento Bruto Mensal", color="Mês")
st.plotly_chart(fig1, use_container_width=True)

## Gráfico 2 - Ticket Médio (usando df_ticket_medio_mensal ordenado)
st.subheader("Ticket Médio Mensal")
# Ajustar o nome da coluna 'TicketMedio' se necessário, com base no seu Excel
# Garantir que seja uma linha com marcadores
fig2 = px.line(df_ticket_medio_mensal, x="Mês", y="Valor Total Mensalidade", markers=True,
               title="Ticket Médio Mensal") # Ajustado para o nome da coluna correto
st.plotly_chart(fig2, use_container_width=True)

## Gráfico 3 - Receitas vs Despesas (para os meses selecionados)
st.subheader(f"Receitas vs Despesas - {' / '.join(meses_selecionados_extenso)}")
# Agrupar e somar receitas e despesas APENAS para os meses filtrados
# Certifique-se de que 'Tipo' está no df_filtrado antes de agrupar
df_agg_filtrado = df_filtrado.groupby(['Mês Nome Extenso', 'Tipo'])['Valor total recebido da parcela (R$)'].sum().reset_index() # Agrupar por Mês e Tipo
# Adicionar a soma das despesas, se a coluna existir e garantir que a coluna de valor seja consistente para o gráfico
if 'Valor total pago da parcela (R$)' in df_filtrado.columns:
     df_agg_filtrado_despesas = df_filtrado.groupby(['Mês Nome Extenso', 'Tipo'])['Valor total pago da parcela (R$)'].sum().reset_index().rename(columns={'Valor total pago da parcela (R$)': 'Valor total recebido da parcela (R$)'}) # Renomear para consistência
     df_agg_filtrado = pd.concat([df_agg_filtrado, df_agg_filtrado_despesas], ignore_index=True)

# Modificado para gráfico de barras agrupadas
fig3 = px.bar(df_agg_filtrado, x="Mês Nome Extenso", y="Valor total recebido da parcela (R$)", color="Tipo",
             barmode='group', # Group the bars side by side
             title=f"Receitas vs Despesas - {' / '.join(meses_selecionados_extenso)}") # Ajustado para a coluna correta e barmode
# Ordenar o eixo X pelos meses selecionados
fig3.update_xaxes(categoryorder='array', categoryarray=meses_selecionados_extenso)

st.plotly_chart(fig3, use_container_width=True)


## Gráfico 4 - Lucratividade Mensal (usando df_faturamento_mensal ordenado e corrigindo y)
st.subheader("Lucratividade Mensal")
# Criando o gráfico de barras e linha sobreposta usando Plotly Go
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


## Gráfico 5 - Churn Rate (usando df_churn_rate_resumo ordenado)
st.subheader("Taxa de Rotatividade (Churn Rate) Mensal")
# Adicionado gráfico de pizza para Churn Rate
# Ajustar o nome da coluna 'ChurnRate' se necessário, com base no seu Excel
fig5 = px.pie(df_churn_rate_resumo, values='Identificador do cliente', names='Mês',
             title='Taxa de Rotatividade (Churn Rate) por Mês')

# Atualiza os traços para mostrar o percentual real de churn rate para cada mês
# Precisamos formatar os valores de churn rate como strings com '%'
# Certifique-se que a coluna de valores no df_churn_rate_resumo é a correta para o cálculo do percentual na pizza
# Assumindo que 'Identificador do cliente' no df_churn_rate_resumo representa o valor para o cálculo do percentual
total_churn = df_churn_rate_resumo['Identificador do cliente'].sum()
churn_rate_labels = [f'{val/total_churn:.1%}' for val in df_churn_rate_resumo['Identificador do cliente'].values]

fig5.update_traces(textinfo='percent+label', insidetextorientation='radial', text=churn_rate_labels) # Usar percent+label para mostrar ambos

# Atualiza o layout para alterar o tamanho da fonte do título e deixá-lo em negrito
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
            'weight': 'bold' # Deixa o título em negrito
        }
    }
)
st.plotly_chart(fig5, use_container_width=True)


## Gráfico 6 - Cancelamentos (usando df_clientes_cancelados_detalhe e df_cancelamentos_resumo)
st.subheader("Cancelamentos Mês a Mês")
# Adicionado gráfico de boxplot para Cancelamentos
# Usar df_clientes_cancelados_detalhe para o boxplot, que contém os valores individuais por cancelamento
# Mapear o mês original para o nome extenso para o eixo X
df_clientes_cancelados_detalhe['Mês Nome Extenso'] = df_clientes_cancelados_detalhe['Mês'].map(meses_extenso)

# Criar o boxplot usando Plotly Express
# Certifique-se que a coluna 'Valor total recebido da parcela (R$)' existe neste DataFrame
if 'Valor total recebido da parcela (R$)' in df_clientes_cancelados_detalhe.columns:
    fig6 = px.box(df_clientes_cancelados_detalhe, x='Mês Nome Extenso', y='Valor total recebido da parcela (R$)',
                  title='Cancelamentos Mês a Mês - Distribuição de Valores',
                  category_orders={'Mês Nome Extenso': [meses_extenso[m] for m in month_order]}) # Ordenar os meses

    st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning("Coluna 'Valor total recebido da parcela (R$)' não encontrada no DataFrame de detalhes dos clientes cancelados para o boxplot.")


# --- Rodapé com dados detalhados ---
st.subheader(f"📑 Dados Detalhados dos Meses Selecionados")

# Exibir apenas as colunas relevantes e renomeá-las para melhor visualização, se necessário
colunas_detalhes = ['Identificador do cliente', 'Nome do cliente', 'Descrição', 'Valor total recebido da parcela (R$)', 'Categoria 1', 'Valor na Categoria 1', 'Mês Nome Extenso'] # Exemplo
df_detalhes_filtrado = df_filtrado[colunas_detalhes].copy()
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

# Exibir detalhes dos clientes cancelados para os meses selecionados
st.subheader(f"❌ Detalhes dos Clientes Cancelados nos Meses Selecionados")

# Filtrar o DataFrame de detalhes dos cancelados pelos meses selecionados
df_cancelados_mes = df_clientes_cancelados_detalhe[df_clientes_cancelados_detalhe['Mês'].isin(meses_selecionados_original)].copy()

# Exibir as colunas relevantes para os detalhes dos cancelados
colunas_cancelados = ['Identificador do cliente', 'Nome do cliente', 'Descrição', 'Valor total recebido da parcela (R$)', 'Mês Nome Extenso'] # Incluir Mês Nome Extenso
df_cancelados_mes_detalhes = df_cancelados_mes[colunas_cancelados].copy()

# Opcional: Renomear colunas para português
df_cancelados_mes_detalhes.rename(columns={
    'Identificador do cliente': 'ID Cliente',
    'Nome do cliente': 'Nome Cliente',
    'Descrição': 'Descrição',
    'Valor total recebido da parcela (R$)': 'Valor Recebido (R$)',
    'Mês Nome Extenso': 'Mês'
}, inplace=True)

st.dataframe(df_cancelados_mes_detalhes)