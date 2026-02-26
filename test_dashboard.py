import streamlit as st

st.title("🧪 Test Dashboard")

st.write("Verificando secrets...")

if "lancamentos_csv" in st.secrets:
    st.success("✅ lancamentos_csv encontrado!")
    st.write(f"Tamanho: {len(st.secrets['lancamentos_csv'])} caracteres")
else:
    st.error("❌ lancamentos_csv NÃO encontrado!")

if "categoria_tipo_csv" in st.secrets:
    st.success("✅ categoria_tipo_csv encontrado!")
else:
    st.error("❌ categoria_tipo_csv NÃO encontrado!")

if "categoria_risco_csv" in st.secrets:
    st.success("✅ categoria_risco_csv encontrado!")
else:
    st.error("❌ categoria_risco_csv NÃO encontrado!")

st.write("Teste completo!")
