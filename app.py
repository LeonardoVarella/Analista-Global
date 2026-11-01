import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard Global de Trading", page_icon="📈", layout="wide")

# Suas credenciais do Supabase
SUPABASE_URL = "https://fcicgdrdxszdkyunywiu.supabase.co"
SUPABASE_KEY = "sb_publishable_tMi8XsWPubFAqXeDpnEN0A_L1x2SJC_"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# Função para carregar os dados do banco em tempo real
@st.cache_data(ttl=5)
def carregar_dados():
    response = supabase.table("alertas_ea").select("*").order("created_at", desc=True).limit(2000).execute()
    return pd.DataFrame(response.data)

st.title("🌐 Dashboard Global de Trading - Alertas MQL5")
st.markdown("Monitoramento em tempo real dos ativos globais enviados pelo seu EA no MetaTrader 5.")

df = carregar_dados()

if df.empty:
    st.warning("⚠️ Nenhum alerta encontrado no banco de dados ainda. Assim que o seu EA disparar o primeiro sinal no MT5, ele aparecerá aqui automaticamente!")
else:
    # Barra lateral de filtros interativos
    st.sidebar.header("🔍 Filtros Globais")
    
    ativos_disponiveis = sorted(df["ativo"].unique().tolist())
    ativo_selecionado = st.sidebar.multiselect("Filtrar por Ativos:", ativos_disponiveis, default=ativos_disponiveis)
    
    # Métricas superiores de resumo
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alertas Registrados", len(df))
    col2.metric("Ativos Distintos Monitorados", df["ativo"].nunique())
    col3.metric("Último Alerta", str(df["created_at"].max())[:19] if not df.empty else "-")
    
    st.markdown("---")
    
    # Filtro aplicado
    df_filtrado = df[df["ativo"].isin(ativo_selecionado)]
    
    # Gráfico e Tabela lado a lado
    col_graf, col_tab = st.columns([2, 1])
    
    with col_graf:
        st.subheader("📊 Frequência de Alertas por Ativo")
        if not df_filtrado.empty:
            fig = px.bar(df_filtrado.groupby("ativo").size().reset_index(name="Quantidade"), 
                         x="ativo", y="Quantidade", color="ativo", 
                         title="Ativos com Mais Oportunidades Mapeadas")
            st.plotly_chart(fig, use_container_width=True)
            
    with col_tab:
        st.subheader("📋 Últimos Disparos")
        st.dataframe(df_filtrado[["created_at", "ativo", "zona_macro", "preco_atual"]], height=350)
        
    st.subheader("📜 Histórico Completo na Nuvem")
    st.dataframe(df_filtrado, use_container_width=True)
