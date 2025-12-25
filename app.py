import streamlit as st
import random
from collections import Counter
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mega Blindada", page_icon="💰", layout="wide")

# Estilo CSS para as bolinhas (Verde Mega Sena)
st.markdown("""
    <style>
    .bolinha {
        display: inline-block;
        width: 45px;
        height: 45px;
        line-height: 45px;
        border-radius: 50%;
        background-color: #209869;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin: 5px;
        border: 2px solid #145d41;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .container-jogo {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #209869;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DADOS (HISTÓRICO) ---
if 'historico' not in st.session_state:
    st.session_state.historico = [
        {"concurso": 2810, "data": "21/12/2025", "dezenas": [4, 12, 32, 45, 49, 58]},
        {"concurso": 2809, "data": "18/12/2025", "dezenas": [1, 15, 23, 33, 42, 50]},
        {"concurso": 2808, "data": "16/12/2025", "dezenas": [10, 22, 35, 44, 51, 60]},
        {"concurso": 2807, "data": "13/12/2025", "dezenas": [5, 18, 27, 40, 48, 59]},
        {"concurso": 2806, "data": "11/12/2025", "dezenas": [2, 11, 28, 37, 43, 55]}
    ]

# --- 3. MOTOR DE FILTRAGEM (REGRAS DO COLAB) ---

def possui_aglomeracao(jogo, limite=3):
    linhas = [(n - 1) // 10 for n in jogo]
    colunas = [(n - 1) % 10 for n in jogo]
    return any(q > limite for q in Counter(linhas).values()) or \
           any(q > limite for q in Counter(colunas).values())

def possui_muitos_finais_iguais(jogo, limite=2):
    return any(q > limite for q in Counter([n % 10 for n in jogo]).values())

def possui_sequencia_longa(jogo, limite=2):
    c = 1
    for i in range(len(jogo) - 1):
        if jogo[i+1] == jogo[i] + 1:
            c += 1
            if c > limite: return True
        else: c = 1
    return False

def gerar_jogo_blindado(ultimos_sorteios):
    viciados = set([n for s in ultimos_sorteios for n in s])
    todos = list(range(1, 61))
    pares = [n for n in todos if n % 2 == 0]
    impares = [n for n in todos if n % 2 != 0]

    while True:
        jogo = sorted(random.sample(pares, 3) + random.sample(impares, 3))
        soma = sum(jogo)
        if not (150 <= soma <= 220): continue
        if possui_sequencia_longa(jogo): continue
        if possui_muitos_finais_iguais(jogo): continue
        if possui_aglomeracao(jogo): continue
        if len([n for n in jogo if n not in viciados]) < 3: continue
        
        status = "⭐ EXCELENTE" if 170 <= soma <= 195 else "✅ BOM"
        dist = f"{len([n for n in jogo if n <= 30])}L / {len([n for n in jogo if n > 30])}H"
        return jogo, soma, dist, status

# --- 4. INTERFACE ---

st.title("💰 Mega Sena Inteligente")

col_input, col_hist = st.columns([1, 1])

with col_input:
    st.subheader("Gerar Sugestões")
    quantidade = st.slider("Quantos jogos?", 1, 15, 5)
    
    if st.button("🚀 Gerar Palpites Blindados"):
        sorteios_numeros = [s["dezenas"] for s in st.session_state.historico]
        
        for i in range(quantidade):
            jogo, soma, dist, status = gerar_jogo_blindado(sorteios_numeros)
            
            # Criar as bolinhas em HTML
            bolinhas_html = "".join([f'<div class="bolinha">{n:02d}</div>' for n in jogo])
            
            # Exibir o jogo com design
            st.markdown(f"""
                <div class="container-jogo">
                    <strong>Jogo {i+1} - {status}</strong><br>
                    {bolinhas_html}<br>
                    <small>Soma: {soma} | Distr: {dist}</small>
                </div>
            """, unsafe_allow_html=True)

with col_hist:
    st.subheader("📊 Histórico Recente")
    df_hist = pd.DataFrame(st.session_state.historico)
    st.dataframe(df_hist, use_container_width=True)

st.divider()
st.caption("Filtros Ativos: 3P/3I, Soma 150-220, Sem sequências longas, Memória de 5 concursos.")
