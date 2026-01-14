import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px

st.set_page_config(layout="wide", page_title="Driva Monitor")
# URL da API
API_URL = os.getenv("API_URL", "http://localhost:3000")

# Título do Dashboard
st.title("📊 Monitoramento de Enriquecimentos")

# Função para buscar dados com tratamento de erro
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

data = get_data("/analytics/overview")

# Indicadores do dashboard 
if data and 'kpis' in data and data['kpis']['total_jobs'] > 0:
    kpis = data['kpis']
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jobs", kpis.get('total_jobs', 0))
    c2.metric("Sucesso", f"{kpis.get('taxa_sucesso', 0)}%")
    c3.metric("Tempo Médio", f"{kpis.get('tempo_medio', 0)} min")
    
    st.divider()
    
    c_chart, c_table = st.columns([1, 2])
    
    with c_chart:
        st.subheader("Distribuição por Tamanho")
        if 'distribuicao' in data:
            df_dist = pd.DataFrame(data['distribuicao'])
            if not df_dist.empty:
                # Geração de um gráfico para a ilustração dos indicadores
                fig = px.pie(df_dist, values='count', names='categoria_tamanho_job', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
    # Geração de uma tabela com os últimos processamentos da camada gold (tratada)        
    with c_table:
        st.subheader("Últimos Processamentos (Camada Gold)")
        details = get_data("/analytics/enrichments")
        if details:
            df = pd.DataFrame(details)
            cols_to_show = ['nome_workspace', 'status_processamento', 'total_contatos', 'duracao_processamento_minutos']
            existing_cols = [c for c in cols_to_show if c in df.columns]
            if existing_cols:
                st.dataframe(df[existing_cols], use_container_width=True)

else:
    st.warning(f"Aguardando dados... (Tentando conectar em: {API_URL})")