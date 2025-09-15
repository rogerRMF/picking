# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Evolução Produção",
                   page_icon="📊", layout="wide")

st.title("Produção hora a hora picking")

# --- CSS GLOBAL ---
st.markdown(
    """
    <style>
    .stApp { background-color: rgb(245,247,249); }
    h1, h2, h3, h4, h5, h6 { font-family: "Arial", sans-serif; }
    .titulo-principal { color: rgb(43,62,76); text-align: left; font-size: 28px; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: rgb(43,62,76); }
    [data-testid="stSidebar"] * { color: rgb(242,239,242) !important; }
    .metric-card { background-color: #fff; border-radius: 15px; padding: 10px; text-align: center; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
col_logo, col_texto = st.sidebar.columns([1, 3])
with col_logo:
    st.image("logo.png", width=40)
with col_texto:
    st.markdown("<b>Evolução Produção</b>", unsafe_allow_html=True)

# Upload CSV/Excel
arquivo = st.sidebar.file_uploader(
    "Selecione um arquivo CSV ou Excel", type=["csv", "xls", "xlsx"])

if arquivo is not None:
    try:
        # --- Leitura do arquivo ---
        try:
            df = pd.read_csv(arquivo, sep=";", header=None,
                             encoding="utf-8", engine="python")
        except Exception:
            arquivo.seek(0)
            try:
                df = pd.read_csv(arquivo, sep=";", header=None,
                                 encoding="latin1", engine="python")
            except Exception:
                arquivo.seek(0)
                try:
                    df = pd.read_csv(arquivo, sep=",", header=None,
                                     encoding="utf-8", engine="python")
                except Exception:
                    arquivo.seek(0)
                    df = pd.read_csv(arquivo, sep=",", header=None,
                                     encoding="latin1", engine="python")

        if df is None or df.empty:
            arquivo.seek(0)
            df = pd.read_excel(arquivo, header=None)

        # --- Tratamento das colunas ---
        df = df.drop(df.columns[[1, 2, 3]], axis=1,
                     errors="ignore")  # remove colunas B, C, D
        df = df.iloc[:, :10]  # mantém até coluna J

        # Renomeia colunas: Usuario + horas
        horas = [f"{str(h).zfill(2)}:00" for h in range(len(df.columns)-1)]
        novos_nomes = ["Usuario"] + horas
        df.columns = novos_nomes

        # Remove duplicadas e converte para número
        df = df.drop_duplicates(subset=["Usuario"], keep="first")
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Elimina a primeira linha (índice 0)
        df = df.iloc[1:]

        # Soma hora a hora por usuário
        df_soma = df.groupby("Usuario").sum().reset_index()

        # Mostra tabela com usuários únicos
        #st.markdown("### 📊 Usuários únicos")
        #st.dataframe(df[["Usuario"]], use_container_width=True)

        # Calcula total geral por usuário
        df_soma["Total"] = df_soma.iloc[:, 1:].sum(axis=1)
        resumo = df_soma[["Usuario", "Total"]].sort_values(
            by="Total", ascending=False)

        # Exibe a tabela completa processada
       # st.markdown("### 📋 Tabela Completa Processada")
       # st.dataframe(df_soma, use_container_width=True)

        # --- Cards de produção total por usuário ---
        st.markdown("### ✅ Produção Total por Usuário")
        icones = ["🟢", "🔵", "🟡", "🟠", "🔴", "🟣", "⚪", "⚫"]
        cols = st.columns(len(resumo))

        for i, row in resumo.iterrows():
            icone = icones[i % len(icones)]
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="metric-card" style="padding:6px; border-radius:10px;">
                        <h4 style="margin:0; font-size:14px;">{icone} {row['Usuario']}</h4>
                        <h3 style="margin:0; font-size:18px;">{int(row['Total'])}</h3>
                  
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")
        # --- Produção hora a hora por usuário ---
        st.markdown("### ⏱ Produção Hora a Hora por Usuário")

        # Define quantas horas por linha
        horas_por_linha = 6

        for _, linha in df_soma.iterrows():
            st.markdown(f"#### 👤 {linha['Usuario']}")

            # Pega todas as colunas de hora, exceto Usuario e Total
            horas = [c for c in df_soma.columns if c not in ["Usuario", "Total", "06:00", "07:00", "08:00"]]

            # Quebra em blocos de horas
            for i in range(0, len(horas), horas_por_linha):
                bloco = horas[i:i+horas_por_linha]
                cols = st.columns(len(bloco))
                for j, hora in enumerate(bloco):
                    valor = int(linha[hora])
                    with cols[j]:
                        st.markdown(
                           f"""
                           <div class="metric-card" style="
                                background-color:#f7f7f7;
                                color:#333;
                                padding:4px;
                                border-radius:10px;
                                width:70px;
                                min-width:70px;
                                max-width:70px;
                                margin:auto;
                                box-shadow: 1px 1px 4px rgba(0,0,0,0.08);
                                text-align:center;
                            ">
                                <h4 style="font-size:14px; margin:0;">{hora}</h4>
                                <h2 style="font-size:18px; margin:0;">{valor}</h2>
                            </div>
                            """,
                            unsafe_allow_html=True
                    )

        st.markdown("---")

    except Exception as e:
        st.error(f"⚠ Erro ao processar o arquivo: {e}")


st.markdown(
    """
    <div style="text-align: center; font-size: 10px;">
        Copyright ©-2025 Direitos Autorais Desenvolvedor Rogério Ferreira
    </div>
    """,
    unsafe_allow_html=True
)
