import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Simulador S&P 500 by Sandreke", page_icon="📈", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0e1a; color: #e8ecf4; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; }
.stApp { background-color: #0a0e1a; }

.hero {
    background: linear-gradient(135deg, #0d1b3e 0%, #0a2a1f 100%);
    border: 1px solid #1e3a5f; border-radius: 16px;
    padding: 2.2rem 2rem 1.8rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,255,128,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: #fff; margin: 0 0 0.3rem; }
.hero-sub { font-weight: 300; color: #7a9bb5; font-size: 0.95rem; letter-spacing: 0.5px; }
.hero-desc { margin-top: 0.8rem; color: #9ab5cc; font-size: 0.88rem; line-height: 1.6; }

/* Input boxes con outline azul prominente */
div[data-testid="stNumberInput"] input {
    background: #0f1729 !important;
    border: 2px solid #4d9fff !important;
    color: #e8ecf4 !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1.1rem !important;
    padding: 0.6rem 0.8rem !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #00d98b !important;
    box-shadow: 0 0 0 3px rgba(0,217,139,0.15) !important;
    outline: none !important;
}
div[data-testid="stNumberInput"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    text-transform: uppercase; letter-spacing: 1px; color: #7a9bb5 !important;
}
div[data-testid="stSlider"] > div { accent-color: #00d98b; }

.section-label {
    font-size: 0.73rem; text-transform: uppercase; letter-spacing: 1.5px;
    color: #4d9fff; font-family: 'DM Mono', monospace;
    margin: 1.5rem 0 0.8rem; border-left: 3px solid #4d9fff; padding-left: 0.6rem;
}

/* Tarjeta central con valor final */
.result-card {
    background: linear-gradient(145deg, #071a12, #0a2a1f);
    border: 1px solid rgba(0,217,139,0.35); border-radius: 20px;
    padding: 2.5rem 2rem 2rem; margin: 1.5rem 0 0.5rem; text-align: center;
    box-shadow: 0 0 40px rgba(0,217,139,0.07);
}
.result-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; color: #5aaa88; font-family: 'DM Mono', monospace; }
.result-value {
    font-family: 'DM Serif Display', serif; font-size: 4rem;
    color: #00d98b; line-height: 1.1; margin: 0.2rem 0 0.1rem;
    text-shadow: 0 0 30px rgba(0,217,139,0.3);
}
.result-mult { font-size: 0.9rem; color: #4a9a70; letter-spacing: 0.3px; }

/* Grid de 4 métricas pequeñas debajo */
.mini-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.7rem; margin: 0.8rem 0 1.5rem; }
.mini-card { background: #0d1424; border: 1px solid #1a2a40; border-radius: 10px; padding: 0.85rem 0.6rem; text-align: center; }
.mini-label { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 1px; color: #4a6a88; font-family: 'DM Mono', monospace; margin-bottom: 0.35rem; }
.mini-value { font-family: 'DM Mono', monospace; font-size: 0.95rem; font-weight: 500; }
.green { color: #00d98b; } .blue { color: #4d9fff; } .white { color: #e8ecf4; } .yellow { color: #f5c842; }

hr { border-color: #1a2540; margin: 1.2rem 0; }

.info-box {
    background: #0d1b3e; border: 1px solid #1e3a6e; border-radius: 10px;
    padding: 0.8rem 1rem; font-size: 0.78rem; color: #5a7a99;
    font-family: 'DM Mono', monospace; margin-top: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def descargar_sp500(años: int) -> pd.DataFrame:
    fin = datetime.today()
    inicio = fin - timedelta(days=años * 365)
    return yf.download("^GSPC", start=inicio, end=fin, auto_adjust=True, progress=False)

def calcular_cagr(df: pd.DataFrame) -> float:
    p0, p1 = float(df["Close"].iloc[0]), float(df["Close"].iloc[-1])
    n = (df.index[-1] - df.index[0]).days / 365.25
    return (p1 / p0) ** (1 / n) - 1

def proyeccion_mensual(P: float, r: float, n: int) -> pd.DataFrame:
    # FV = P * ((1+r)^n - 1) / r aplicado mes a mes
    meses = np.arange(1, n + 1)
    return pd.DataFrame({
        "Mes": meses,
        "Valor": P * ((1 + r) ** meses - 1) / r,
        "Aportado": P * meses,
    })


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">Simulador del S&amp;P 500 by Sandreke</div>
  <div class="hero-sub">Lo que ganarías invirtiendo mensualmente</div>
  <div class="hero-desc">
    Indica cuánto invertir cada mes y durante cuántos años. La app descarga datos reales del S&amp;P 500,
    calcula el rendimiento anual histórico (CAGR) y simula cómo crecería tu dinero aplicando
    interés compuesto.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Slider base histórica ─────────────────────────────────────────────────────
st.markdown('<div class="section-label">⚙ Base histórica para el cálculo</div>', unsafe_allow_html=True)
años_hist = st.slider("Años de historia del S&P 500", 5, 30, 15, 1,
                      help="Período usado para calcular el rendimiento anual promedio (CAGR).")

with st.spinner("Descargando datos reales del S&P 500..."):
    try:
        df_hist = descargar_sp500(años_hist)
        cagr = calcular_cagr(df_hist)
        r_mensual = (1 + cagr) ** (1 / 12) - 1
        data_ok = True
    except Exception as e:
        st.error(f"Error al descargar datos: {e}")
        data_ok = False

if not data_ok:
    st.stop()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">💰 Parámetros de inversión</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    aporte = st.number_input("Aporte mensual ($)", min_value=1.0, max_value=100_000.0,
                             value=500.0, step=50.0, format="%.0f")
with col2:
    años_inv = st.number_input("Años a invertir", min_value=1, max_value=50, value=20, step=1)

# ── Cálculos ──────────────────────────────────────────────────────────────────
n_meses       = int(años_inv * 12)
df_ev         = proyeccion_mensual(aporte, r_mensual, n_meses)
total_aportado = aporte * n_meses
valor_final   = float(df_ev["Valor"].iloc[-1])
ganancia      = valor_final - total_aportado
multiplicador = valor_final / total_aportado

# ── Valor final prominente ────────────────────────────────────────────────────
st.markdown(f"""
<div class="result-card">
  <div class="result-label">Valor final acumulado</div>
  <div class="result-value">${valor_final:,.0f}</div>
</div>
""", unsafe_allow_html=True)

# ── 4 métricas secundarias ────────────────────────────────────────────────────
st.markdown(f"""
<div class="mini-grid">
  <div class="mini-card">
    <div class="mini-label">CAGR histórico</div>
    <div class="mini-value green">{cagr*100:.2f}%</div>
  </div>
  <div class="mini-card">
    <div class="mini-label">Tasa mensual</div>
    <div class="mini-value blue">{r_mensual*100:.4f}%</div>
  </div>
  <div class="mini-card">
    <div class="mini-label">Ganancia generada</div>
    <div class="mini-value yellow">+${ganancia:,.0f}</div>
  </div>
  <div class="mini-card">
    <div class="mini-label">Total aportado</div>
    <div class="mini-value white">${total_aportado:,.0f}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Gráfico de crecimiento ────────────────────────────────────────────────────
st.markdown('<div class="section-label">📊 Evolución del portafolio</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_ev["Mes"] / 12, y=df_ev["Valor"],
    fill="tozeroy", fillcolor="rgba(0,217,139,0.10)",
    line=dict(color="#00d98b", width=2.5), name="Valor acumulado",
    hovertemplate="Año %{x:.1f}<br>Valor: $%{y:,.0f}<extra></extra>"
))
fig.add_trace(go.Scatter(
    x=df_ev["Mes"] / 12, y=df_ev["Aportado"],
    fill="tozeroy", fillcolor="rgba(77,159,255,0.10)",
    line=dict(color="#4d9fff", width=1.5, dash="dot"), name="Total aportado",
    hovertemplate="Año %{x:.1f}<br>Aportado: $%{y:,.0f}<extra></extra>"
))
fig.update_layout(
    paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1729",
    font=dict(family="DM Mono, monospace", color="#7a9bb5", size=11),
    legend=dict(bgcolor="#0f1729", bordercolor="#1e2d4a", borderwidth=1, font=dict(color="#e8ecf4")),
    xaxis=dict(title="Años", gridcolor="#1a2540", zerolinecolor="#1a2540", ticksuffix=" a"),
    yaxis=dict(title="USD", gridcolor="#1a2540", zerolinecolor="#1a2540", tickprefix="$", tickformat=",.0f"),
    hovermode="x unified", margin=dict(l=10, r=10, t=20, b=10), height=360,
)
st.plotly_chart(fig, use_container_width=True)

# ── Histórico real (colapsable) ───────────────────────────────────────────────
with st.expander("Ver precio histórico real del S&P 500"):
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_hist.index, y=df_hist["Close"].squeeze(),
        line=dict(color="#4d9fff", width=1.8),
        fill="tozeroy", fillcolor="rgba(77,159,255,0.07)",
        hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1729",
        font=dict(family="DM Mono, monospace", color="#7a9bb5", size=11),
        xaxis=dict(gridcolor="#1a2540"), yaxis=dict(gridcolor="#1a2540", tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=10), height=260, showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="info-box">
⚠ Simulación basada en el CAGR histórico del S&P 500. Rendimientos pasados no garantizan resultados futuros. No constituye asesoramiento financiero.
</div>
""", unsafe_allow_html=True)