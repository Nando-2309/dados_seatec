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
    # Carregar os DataFrames que contêm os dados já processados e resumidos
    df_faturamento_mensal = pd.read_excel(file_path, sheet_name="Faturamento Mensal")
    df_cancelamentos_resumo = pd.read_excel(file_path, sheet_name="Cancelamentos Resumo")
    df_churn_rate_resumo = pd.read_excel(file_path, sheet_name="Churn Rate Resumo")
    df_clientes_cancelados_detalhe = pd.read_excel(file_path, sheet_name="Clientes Cancelados Detalhe")
    df_receita_mensal_resumo = pd.read_excel(file_path, sheet_name="Receita Mensal Resumo")
    df_ticket_medio_mensal_resumo = pd.read_excel(file_path, sheet_name="Ticket Medio Mensal Resumo") # Carregar o ticket médio resumido

except FileNotFoundError:
    st.error(f"Erro: O arquivo {file_path} não foi encontrado. Certifique-se de que o arquivo está no diretório correto.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo Excel: {e}")
    st.stop()


# --- Preparar dados ---
# Mapeamento meses por extenso para ordenação e exibição
month_order_original = ['abril', 'maio', 'junho', 'julho', 'agosto'] # Ordem original dos meses
meses_extenso = {
    'abril': 'Abril', 'maio': 'Maio', 'junho': 'Junho',
    'julho': 'Julho', 'agosto': 'Agosto'
}
month_order_capitalized = [meses_extenso[m] for m in month_order_original] # Ordem dos meses capitalizados

# Aplicar ordenação categórica aos DataFrames carregados inicialmente
for df_resumo in [df_faturamento_mensal, df_cancelamentos_resumo, df_churn_rate_resumo, df_receita_mensal_resumo, df_ticket_medio_mensal_resumo]:
    if 'Mês' in df_resumo.columns:
        df_resumo['Mês'] = df_resumo['Mês'].map(meses_extenso).fillna(df_resumo['Mês']) # Mapeia se for o nome original, senão mantém
        df_resumo['Mês'] = pd.Categorical(df_resumo['Mês'], categories=month_order_capitalized, ordered=True)
        df_resumo = df_resumo.sort_values('Mês') # Ordenar pelo mês

# Garantir que a coluna 'Mês' no df_clientes_cancelados_detalhe esteja em português (capitalizada) para o boxplot e tabela de detalhes
if 'Mês' in df_clientes_cancelados_detalhe.columns:
    df_clientes_cancelados_detalhe['Mês Nome Extenso'] = df_clientes_cancelados_detalhe['Mês'].map(meses_extenso)
    # Não precisa categorizar e ordenar aqui, pois o Plotly Express fará isso com base em category_orders


# --- Sidebar com filtro de mês ---
st.sidebar.header("🔍 Filtros") # Adicionado ícone de lupa

# Obter meses disponíveis do DataFrame de faturamento (já capitalizado e ordenado)
meses_disponiveis_extenso = df_faturamento_mensal['Mês'].unique().tolist()

# Multi-select para meses com todos selecionados por padrão
meses_selecionados_extenso = st.sidebar.multiselect("Selecione o(s) mês(es):", meses_disponiveis_extenso, default=meses_disponiveis_extenso)

# Filtrar DataFrames resumo pelos meses selecionados (comparando com a coluna de mês capitalizado)
df_faturamento_filtrado = df_faturamento_mensal[df_faturamento_mensal['Mês'].isin(meses_selecionados_extenso)].copy()
df_cancelamentos_filtrado = df_cancelamentos_resumo[df_cancelamentos_resumo['Mês'].isin(meses_selecionados_extenso)].copy()
df_churn_rate_filtrado = df_churn_rate_resumo[df_churn_rate_resumo['Mês'].isin(meses_selecionados_extenso)].copy()
df_receita_mensal_filtrado = df_receita_mensal_resumo[df_receita_mensal_resumo['Mês'].isin(meses_selecionados_extenso)].copy()
df_ticket_medio_mensal_filtrado = df_ticket_medio_mensal_resumo[df_ticket_medio_mensal_resumo['Mês'].isin(meses_selecionados_extenso)].copy()


# Aplicar ordenação categórica aos DataFrames FILTRADOS antes de plotar
if not df_faturamento_filtrado.empty:
     df_faturamento_filtrado['Mês'] = pd.Categorical(df_faturamento_filtrado['Mês'], categories=meses_selecionados_extenso, ordered=True)
     df_faturamento_filtrado = df_faturamento_filtrado.sort_values('Mês')

if not df_cancelamentos_filtrado.empty:
    df_cancelamentos_filtrado['Mês'] = pd.Categorical(df_cancelamentos_filtrado['Mês'], categories=meses_selecionados_extenso, ordered=True)
    df_cancelamentos_filtrado = df_cancelamentos_filtrado.sort_values('Mês')

if not df_churn_rate_filtrado.empty:
     df_churn_rate_filtrado['Mês'] = pd.Categorical(df_churn_rate_filtrado['Mês'], categories=meses_selecionados_extenso, ordered=True)
     df_churn_rate_filtrado = df_churn_rate_filtrado.sort_values('Mês')

if not df_receita_mensal_filtrado.empty:
    df_receita_mensal_filtrado['Mês'] = pd.Categorical(df_receita_mensal_filtrado['Mês'], categories=meses_selecionados_extenso, ordered=True)
    df_receita_mensal_filtrado = df_receita_mensal_filtrado.sort_values('Mês')

if not df_ticket_medio_mensal_filtrado.empty:
    df_ticket_medio_mensal_filtrado['Mês'] = pd.Categorical(df_ticket_medio_mensal_filtrado['Mês'], categories=meses_selecionados_extenso, ordered=True)
    df_ticket_medio_mensal_filtrado = df_ticket_medio_mensal_filtrado.sort_values('Mês')


# Inicializar df_clientes_cancelados_detalhe_filtrado como um DataFrame vazio antes de filtrar
df_clientes_cancelados_detalhe_filtrado = pd.DataFrame()

# Filtrar detalhes dos clientes cancelados pelos meses selecionados (comparando com a coluna de mês original)
# Garantir que a coluna 'Mês' no df_clientes_cancelados_detalhe esteja em português (capitalizada) para o boxplot e tabela de detalhes
if 'Mês' in df_clientes_cancelados_detalhe.columns:
    df_clientes_cancelados_detalhe['Mês Nome Extenso'] = df_clientes_cancelados_detalhe['Mês'].map(meses_extenso)
    if meses_selecionados_extenso:
        df_clientes_cancelados_detalhe_filtrado = df_clientes_cancelados_detalhe[df_clientes_cancelados_detalhe['Mês Nome Extenso'].isin(meses_selecionados_extenso)].copy()
        df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'] = pd.Categorical(df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'], categories=meses_selecionados_extenso, ordered=True)
        df_clientes_cancelados_detalhe_filtrado = df_clientes_cancelados_detalhe_filtrado.sort_values('Mês Nome Extenso')
    else:
        df_clientes_cancelados_detalhe_filtrado = pd.DataFrame() # Ensure it's empty if no months selected
else:
     df_clientes_cancelados_detalhe_filtrado = pd.DataFrame() # Ensure it's empty if 'Mês' column is missing

# --- Página principal ---
st.title("📊 Dados da Seatec")

## Gráfico 1 - Faturamento Bruto (usando df_receita_mensal_filtrado)
st.subheader("Faturamento Bruto")
if not df_receita_mensal_filtrado.empty:
    # Renomear a coluna de valor para um nome mais descritivo para o gráfico
    df_receita_mensal_filtrado.rename(columns={'Valor total recebido da parcela (R$)': 'Valor Receita Total (R$)'}, inplace=True)
    fig1 = px.bar(
        df_receita_mensal_filtrado,
        x= "Valor Receita Total (R$)",
        y="Mês",
        orientation='h',
        title="Faturamento Bruto Mensal",
        color="Mês",
        category_orders={"Mês": meses_selecionados_extenso} # Garantir a ordem correta no gráfico
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("Dados de faturamento bruto não disponíveis para os meses selecionados.")


## Gráfico 2 - Ticket Médio (usando df_ticket_medio_mensal_filtrado)
st.subheader("Ticket Médio Mensal")

if not df_ticket_medio_mensal_filtrado.empty:
    # Renomear a coluna de valor para um nome mais descritivo para o gráfico
     df_ticket_medio_mensal_filtrado.rename(columns={'Valor Total Mensalidade': 'Ticket Médio Mensalidade (R$)'}, inplace=True)
    # Criar um gráfico de linha usando Plotly Go (ou Plotly Express para simplicidade)
     fig2 = px.line(df_ticket_medio_mensal_filtrado, x='Mês', y='Ticket Médio Mensalidade (R$)', markers=True)

     fig2.update_layout(
         title='Ticket Médio Mensal',
         xaxis_title='Mês',
         yaxis_title='Ticket Médio (R$)',
         xaxis={'categoryorder':'array', 'categoryarray': meses_selecionados_extenso} # Garantir a ordem no eixo X
     )
     st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Dados de ticket médio não disponíveis para os meses selecionados.")


# --- Gráfico: Receitas vs Despesas (usando df_faturamento_filtrado) ---
st.subheader("Receitas vs Despesas")

# Criar um DataFrame no formato longo para o gráfico de barras agrupado
if not df_faturamento_filtrado.empty:
    df_receitas_despesas_long = df_faturamento_filtrado.melt(
        id_vars="Mês",
        value_vars=["Valor_Receita", "Valor_Despesa"],
        var_name="Tipo",
        value_name="Valor"
    )

    # Mapear 'Tipo' para nomes mais amigáveis e garantir que as despesas sejam positivas para o gráfico
    df_receitas_despesas_long['Tipo'] = df_receitas_despesas_long['Tipo'].map({
        'Valor_Receita': 'Receita',
        'Valor_Despesa': 'Despesa'
    })
    # Certificar que os valores de Despesa são positivos para o gráfico de barras
    df_receitas_despesas_long.loc[df_receitas_despesas_long['Tipo'] == 'Despesa', 'Valor'] = df_receitas_despesas_long.loc[df_receitas_despesas_long['Tipo'] == 'Despesa', 'Valor'].abs()


    # Criar o gráfico de barras agrupado
    fig3 = px.bar(
        df_receitas_despesas_long,
        x="Mês",
        y="Valor",
        color="Tipo",
        barmode="group", # Agrupar as barras lado a lado
        title="Receitas vs Despesas por Mês",
        labels={"Valor": "Valor (R$)", "Mês": "Mês"},
        color_discrete_map={'Receita': 'blue', 'Despesa': 'red'}, # Definir cores
        category_orders={"Mês": meses_selecionados_extenso} # Garantir a ordem correta no gráfico
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
     st.warning("Dados de receitas e despesas não disponíveis para os meses selecionados.")


## Gráfico 4 - Lucratividade Mensal (usando df_faturamento_filtrado)
st.subheader("Lucratividade Mensal")
if not df_faturamento_filtrado.empty:
    # Criando o gráfico de barras e linha sobreposta usando Plotly Go
    fig4 = go.Figure(data=[
        go.Bar(name='Faturamento', x=df_faturamento_filtrado['Mês'], y=df_faturamento_filtrado['Faturamento'], marker_color='blue'),
        go.Scatter(name='Evolução da Lucratividade', x=df_faturamento_filtrado['Mês'], y=df_faturamento_filtrado['Faturamento'], mode='lines+markers', line=dict(color='purple', width=4), marker=dict(color='purple', size=6))
    ])

    # Atualizando o layout
    fig4.update_layout(
        title='Lucratividade Mensal (R$)',
        xaxis_title='Mês',
        yaxis_title='Faturamento (R$)',
        xaxis={'categoryorder':'array', 'categoryarray': meses_selecionados_extenso}, # Garantir a ordem no eixo X
        barmode='overlay' # Para sobrepor a linha nas barras
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("Dados de lucratividade mensal não disponíveis para os meses selecionados.")


## Gráfico 5 - Churn Rate (usando df_churn_rate_filtrado)
st.subheader("Taxa de Rotatividade (Churn Rate) Mensal")
if not df_churn_rate_filtrado.empty:
    # O nome da coluna no excel sheet "Churn Rate Resumo" para os valores é 'Identificador do cliente' (que representa a taxa)
    # Renomear a coluna de valor para um nome mais descritivo para o gráfico
    df_churn_rate_filtrado.rename(columns={'Identificador do cliente': 'Churn Rate (%)'}, inplace=True)

    # Criar a coluna de rótulos com o percentual correto formatado
    df_churn_rate_filtrado['Churn Rate Label'] = df_churn_rate_filtrado['Churn Rate (%)'].apply(lambda x: f'{x:.2f}%')

    fig5 = px.pie(df_churn_rate_filtrado, values='Churn Rate (%)', names='Mês',
             title='Taxa de Rotatividade (Churn Rate) por Mês')

    # Usar a coluna 'Churn Rate Label' para exibir o texto no gráfico
    # textinfo='text' para mostrar apenas o texto personalizado
    fig5.update_traces(textinfo='text', text=df_churn_rate_filtrado['Churn Rate Label'], insidetextorientation='radial')


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
    st.warning("Dados de Churn Rate não disponíveis para os meses selecionados.")


## Gráfico 6 - Cancelamentos (usando df_clientes_cancelados_detalhe_filtrado)
st.subheader("Cancelamentos Mês a Mês")

# Filter the detailed cancelled clients DataFrame after months are selected
if 'Mês' in df_clientes_cancelados_detalhe.columns:
    df_clientes_cancelados_detalhe['Mês Nome Extenso'] = df_clientes_cancelados_detalhe['Mês'].map(meses_extenso)
    if meses_selecionados_extenso:
        df_clientes_cancelados_detalhe_filtrado = df_clientes_cancelados_detalhe[df_clientes_cancelados_detalhe['Mês Nome Extenso'].isin(meses_selecionados_extenso)].copy()
        df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'] = pd.Categorical(df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'], categories=meses_selecionados_extenso, ordered=True)
        df_clientes_cancelados_detalhe_filtrado = df_clientes_cancelados_detalhe_filtrado.sort_values('Mês Nome Extenso')
    else:
        df_clientes_cancelados_detalhe_filtrado = pd.DataFrame() # Ensure it's empty if no months selected
else:
     df_clientes_cancelados_detalhe_filtrado = pd.DataFrame() # Ensure it's empty if 'Mês' column is missing


if not df_clientes_cancelados_detalhe_filtrado.empty:
    # Ensure that the 'Valor total recebido da parcela (R$)' column exists in this DataFrame
    if 'Valor total recebido da parcela (R$)' in df_clientes_cancelados_detalhe_filtrado.columns:

        # Criar o gráfico de boxplot usando Plotly Go sem anotações de nomes
        fig6 = go.Figure()

        # Adicionar um boxplot para cada mês selecionado
        for mes in meses_selecionados_extenso:
            df_mes = df_clientes_cancelados_detalhe_filtrado[df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'] == mes].copy()
            if not df_mes.empty:
                fig6.add_trace(go.Box(
                    y=df_mes['Valor total recebido da parcela (R$)'],
                    name=mes,
                    boxpoints='all', # Mostrar todos os pontos
                    jitter=0.3,       # Adicionar jitter aos pontos
                    pointpos=-1.8     # Posição dos pontos
                ))


        # Atualizar o layout do gráfico
        fig6.update_layout(
            title='Cancelamentos Mês a Mês - Distribuição de Valores',
            xaxis_title='Mês',
            yaxis_title='Valor Recebido da Parcela (R$)',
            xaxis={'categoryorder':'array', 'categoryarray': meses_selecionados_extenso} # Garantir a ordem no eixo X
        )


        st.plotly_chart(fig6, use_container_width=True)

        # Exibir os nomes dos clientes cancelados por mês abaixo do boxplot
        st.subheader("Clientes Cancelados por Mês:")
        if not df_clientes_cancelados_detalhe_filtrado.empty:
             for mes in meses_selecionados_extenso:
                clientes_do_mes = df_clientes_cancelados_detalhe_filtrado[df_clientes_cancelados_detalhe_filtrado['Mês Nome Extenso'] == mes]['Nome do cliente'].tolist()
                if clientes_do_mes:
                    st.write(f"**{mes}:**")
                    for cliente in clientes_do_mes:
                         st.write(f"- {cliente}")
                else:
                    st.write(f"**{mes}:** Nenhum cliente cancelado neste mês.")


    else:
        st.warning("Coluna 'Valor total recebido da parcela (R$)' não encontrada no DataFrame de detalhes dos clientes cancelados para o boxplot.")
elif meses_selecionados_extenso: # Show message only if months are selected but no data
    st.warning("Dados de clientes cancelados não disponíveis para os meses selecionados.")
else: # Show message if no months are selected
    st.info("Selecione os meses na barra lateral para ver os dados de cancelamentos.")


# --- Rodapé com dados detalhados ---
st.subheader(f"📑 Dados Detalhados dos Meses Selecionados")

# Combina os DataFrames de receitas e despesas filtrados para exibir os detalhes
# Precisamos carregar os DataFrames originais de receitas e despesas combinadas para filtrar e exibir
# Como não temos os DataFrames combinados originais carregados no Streamlit,
# vamos readaptar para carregar e filtrar aqui ou assumir que df_combined foi carregado
# (Assumindo que df_combined foi criado anteriormente no notebook e salvo no excel sheet "Receitas Combinadas" e "Despesas Combinadas")
# Se você não tem o df_combined original salvo, você precisará carregar os sheets e concatenar
# Aqui, vamos carregar os sheets combinados do excel file
try:
    df_receitas_combinadas_full = pd.read_excel(file_path, sheet_name="Receitas Combinadas")
    df_despesas_combinadas_full = pd.read_excel(file_path, sheet_name="Despesas Combinadas")

    # Adicionar coluna 'Tipo' para diferenciar receitas e despesas
    df_receitas_combinadas_full["Tipo"] = "Receita"
    df_despesas_combinadas_full["Tipo"] = "Despesa"

    # Concatenar os DataFrames completos
    df_combined_full = pd.concat([df_receitas_combinadas_full, df_despesas_combinadas_full], ignore_index=True)

    # Mapear nome do mês completo para filtro e exibição
    df_combined_full['Mês Nome Extenso'] = df_combined_full['Mês'].map(meses_extenso)

    # Filtrar o DataFrame completo pelos meses selecionados (em nome extenso)
    df_detalhes_filtrado = df_combined_full[df_combined_full["Mês Nome Extenso"].isin(meses_selecionados_extenso)].copy()


    # Exibir apenas as colunas relevantes e renomeá-las para melhor visualização, se necessário
    # Incluindo a coluna 'Tipo' para saber se é Receita ou Despesa
    colunas_detalhes = ['Tipo', 'Identificador do cliente', 'Nome do cliente', 'Identificador do fornecedor', 'Nome do fornecedor',
                        'Descrição', 'Valor total recebido da parcela (R$)', 'Valor total pago da parcela (R$)',
                        'Categoria 1', 'Valor na Categoria 1', 'Mês Nome Extenso']

    # Check if df_detalhes_filtrado is not empty before selecting columns
    if not df_detalhes_filtrado.empty:
        # Ensure all required columns exist before selecting
        required_cols_detalhes = [col for col in colunas_detalhes if col in df_detalhes_filtrado.columns]
        df_detalhes_filtrado = df_detalhes_filtrado[required_cols_detalhes].copy()

        # Opcional: Renomear colunas para português para exibição
        df_detalhes_filtrado.rename(columns={
            'Identificador do cliente': 'ID Cliente',
            'Nome do cliente': 'Nome Cliente',
            'Identificador do fornecedor': 'ID Fornecedor',
            'Nome do fornecedor': 'Nome Fornecedor',
            'Descrição': 'Descrição',
            'Valor total recebido da parcela (R$)': 'Valor Recebido Total (R$)',
            'Valor total pago da parcela (R$)': 'Valor Pago Total (R$)',
            'Categoria 1': 'Categoria Principal',
            'Valor na Categoria 1': 'Valor Categoria Principal (R$)',
            'Mês Nome Extenso': 'Mês'
        }, inplace=True)

        st.dataframe(df_detalhes_filtrado)
    elif meses_selecionados_extenso: # Show message only if months are selected but no data
        st.warning("Dados detalhados não disponíveis para os meses selecionados.")
    else: # Show message if no months are selected
        st.info("Selecione os meses na barra lateral para ver os dados detalhados.")

except FileNotFoundError:
     st.warning(f"Não foi possível carregar os DataFrames combinados originais do arquivo Excel para exibir os detalhes.")
except Exception as e:
    st.error(f"Erro ao carregar os DataFrames combinados originais do arquivo Excel: {e}")


# Exibir detalhes dos clientes cancelados para os meses selecionados (usando df_clientes_cancelados_detalhe_filtrado)
st.subheader(f"❌ Detalhes dos Clientes Cancelados nos Meses Selecionados")

# Check if df_clientes_cancelados_detalhe_filtrado is not empty before displaying
if not df_clientes_cancelados_detalhe_filtrado.empty:
    # Exibir as colunas relevantes para os detalhes dos cancelados
    colunas_cancelados = ['Identificador do cliente', 'Nome do cliente', 'Descrição', 'Valor total recebido da parcela (R$)', 'Mês Nome Extenso'] # Incluir Mês Nome Extenso
    # Ensure all required columns exist before selecting
    required_cols_cancelados = [col for col in colunas_cancelados if col in df_clientes_cancelados_detalhe_filtrado.columns]
    df_cancelados_mes_detalhes = df_clientes_cancelados_detalhe_filtrado[required_cols_cancelados].copy()


    # Opcional: Renomear colunas para português para exibição
    df_cancelados_mes_detalhes.rename(columns={
        'Identificador do cliente': 'ID Cliente',
        'Nome do cliente': 'Nome Cliente',
        'Descrição': 'Descrição',
        'Valor total recebido da parcela (R$)': 'Valor Recebido (R$)',
        'Mês Nome Extenso': 'Mês'
    }, inplace=True)

    st.dataframe(df_cancelados_mes_detalhes)
elif meses_selecionados_extenso: # Show message only if months are selected but no data
    st.warning("Detalhes de clientes cancelados não disponíveis para os meses selecionados.")
else: # Show message if no months are selected
    st.info("Selecione os meses na barra lateral para ver os detalhes dos clientes cancelados.")