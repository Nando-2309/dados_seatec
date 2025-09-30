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

