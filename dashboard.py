import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

#Configuração da página#
st.set_page_config(
    page_title="Dashboard de Investimentos",
    page_icon="💰",
    layout="wide"
)

#Título#
st.title("💰 Dashboard de Investimentos")
st.markdown("---")

#Conectar ao DuckDB#
@st.cache_resource
def get_connection():
    return duckdb.connect('investimentos.db')

conn = get_connection()

#Query 1: Saldo total atual#
@st.cache_data
def get_saldo_total():
    query = """
    SELECT SUM(valor) as saldo_total
    FROM lancamentos
    WHERE tipo_transacao = 'Saldo'
    """
    return conn.execute(query).fetchdf()

#Query 2: Distribuição por tipo#
@st.cache_data
def get_distribuicao_tipo():
    query = """
    SELECT 
        ct.tipo_de_investimento,
        ROUND(SUM(l.valor), 2) as saldo_total,
        COUNT(*) as qtd_investimentos
    FROM lancamentos l
    LEFT JOIN categoria_tipo ct ON l.nome = ct.nome
    WHERE l.tipo_transacao = 'Saldo'
    GROUP BY ct.tipo_de_investimento
    ORDER BY saldo_total DESC
    """
    return conn.execute(query).fetchdf()

#Query 3: Distribuição por risco#
@st.cache_data
def get_distribuicao_risco():
    query = """
    SELECT 
        cr.risco,
        ROUND(SUM(l.valor), 2) as saldo_total
    FROM lancamentos l
    LEFT JOIN categoria_tipo ct ON l.nome = ct.nome
    LEFT JOIN categoria_risco cr ON ct.tipo_de_investimento = cr.tipo_de_investimento
    WHERE l.tipo_transacao = 'Saldo'
    GROUP BY cr.risco
    ORDER BY saldo_total DESC
    """
    return conn.execute(query).fetchdf()

#Query 4: Rendimento anualizado#
@st.cache_data
def get_rendimento_anualizado():
    query = """
    WITH primeiro_aporte AS (
        SELECT nome, MIN(data) as data_inicial
        FROM lancamentos
        WHERE tipo_transacao = 'Aporte'
        GROUP BY nome
    ),
    saldo_atual AS (
        SELECT DISTINCT ON (nome)
            nome, data as data_final, valor as saldo_final
        FROM lancamentos
        WHERE tipo_transacao = 'Saldo'
        ORDER BY nome, data DESC
    ),
    movimentacoes AS (
        SELECT 
            nome,
            SUM(CASE WHEN tipo_transacao = 'Aporte' THEN valor ELSE 0 END) as total_aportes,
            SUM(CASE WHEN tipo_transacao = 'Resgate' THEN valor ELSE 0 END) as total_resgates
        FROM lancamentos
        GROUP BY nome
    )
    SELECT 
        pa.nome,
        ct.tipo_de_investimento,
        cr.risco,
        pa.data_inicial,
        sa.data_final,
        ROUND(DATEDIFF('day', pa.data_inicial, sa.data_final) / 365.25, 2) as anos_investido,
        ROUND(m.total_aportes, 2) as total_aportes,
        ROUND(sa.saldo_final, 2) as saldo_final,
        ROUND(sa.saldo_final - m.total_aportes + m.total_resgates, 2) as rendimento_total,
        ROUND(((sa.saldo_final - m.total_aportes + m.total_resgates) / m.total_aportes) * 100, 2) as rendimento_percent,
        ROUND((POWER((sa.saldo_final / m.total_aportes), (1.0 / NULLIF(DATEDIFF('day', pa.data_inicial, sa.data_final) / 365.25, 0))) - 1) * 100, 2) as rendimento_anual
    FROM primeiro_aporte pa
    JOIN saldo_atual sa ON pa.nome = sa.nome
    JOIN movimentacoes m ON pa.nome = m.nome
    LEFT JOIN categoria_tipo ct ON pa.nome = ct.nome
    LEFT JOIN categoria_risco cr ON ct.tipo_de_investimento = cr.tipo_de_investimento
    ORDER BY rendimento_anual DESC
    """
    return conn.execute(query).fetchdf()

#Carregar dados#
df_saldo = get_saldo_total()
df_tipo = get_distribuicao_tipo()
df_risco = get_distribuicao_risco()
df_rendimento = get_rendimento_anualizado()

#KPI: Saldo Total#
col1, col2, col3 = st.columns(3)

with col1:
    saldo_total = df_saldo['saldo_total'].iloc[0]
    st.metric(
        label="💰 Patrimônio Total",
        value=f"R$ {saldo_total:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    )

with col2:
    total_investimentos = df_rendimento.shape[0]
    st.metric(
        label="📊 Total de Investimentos",
        value=total_investimentos
    )

with col3:
    rendimento_total = df_rendimento['rendimento_total'].sum()
    st.metric(
        label="📈 Rendimento Total Acumulado",
        value=f"R$ {rendimento_total:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    )

st.markdown("---")

#Gráficos lado a lado#
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribuição por Tipo de Investimento")
    fig_tipo = px.pie(
        df_tipo,
        values='saldo_total',
        names='tipo_de_investimento',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_tipo, use_container_width=True)

with col2:
    st.subheader("🎯 Distribuição por Nível de Risco")
    fig_risco = px.pie(
        df_risco,
        values='saldo_total',
        names='risco',
        hole=0.4,
        color_discrete_map={'baixo': '#90EE90', 'alto': '#FFB6C6'}
    )
    fig_risco.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_risco, use_container_width=True)

st.markdown("---")

#Tabela de rendimentos#
st.subheader("🏆 Performance dos Investimentos (Rendimento Anualizado)")

#Formatação da tabela#
df_display = df_rendimento.copy()
df_display['saldo_final'] = df_display['saldo_final'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
df_display['total_aportes'] = df_display['total_aportes'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
df_display['rendimento_total'] = df_display['rendimento_total'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
df_display['rendimento_percent'] = df_display['rendimento_percent'].apply(lambda x: f"{x:.2f}%")
df_display['rendimento_anual'] = df_display['rendimento_anual'].apply(lambda x: f"{x:.2f}% a.a.")

#Renomear colunas#
df_display = df_display[[
    'nome', 'tipo_de_investimento', 'risco', 'anos_investido',
    'total_aportes', 'saldo_final', 'rendimento_total',
    'rendimento_percent', 'rendimento_anual'
]]

df_display.columns = [
    'Investimento', 'Tipo', 'Risco', 'Anos', 
    'Aportes', 'Saldo Atual', 'Rendimento (R$)',
    'Rendimento (%)', 'Rendimento Anual'
]

st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("💡 Atualize seus dados mensalmente nos CSVs e o dashboard refletirá automaticamente as mudanças!")