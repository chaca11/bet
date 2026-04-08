import streamlit as st
import numpy as np
import requests
from datetime import datetime, timedelta
import time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Betting Tool PRO", layout="centered")

API_KEY = st.secrets["API_KEY"]  # 🔐 usa secrets

# =========================
# ESTILOS PRO
# =========================
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
}
.card {
    padding: 15px;
    border-radius: 15px;
    background-color: #111;
    color: white;
    text-align: center;
    margin-bottom: 10px;
}
.pick {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
}
.good { background-color: #0f5132; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚽ Betting Tool PRO</div>', unsafe_allow_html=True)

# =========================
# LOADER
# =========================
st.markdown("""
<style>
.loader {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #00ff99;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# API MATCHES
# =========================
@st.cache_data(ttl=3600)
def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    params = {
        "dateFrom": datetime.today().strftime('%Y-%m-%d'),
        "dateTo": (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    leagues = {}

    for match in data.get("matches", []):
        league = match["competition"]["name"]
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        match_name = f"{home} vs {away}"

        if league not in leagues:
            leagues[league] = {}

        leagues[league][match_name] = {
            "home": home,
            "away": away,
            "league": league
        }

    return leagues

# =========================
# MODELO
# =========================
def estimate_xg(team):
    top = ["Real Madrid", "Manchester City", "Bayern Munich",
           "Barcelona", "PSG", "Arsenal", "Liverpool"]
    return 2.0 if team in top else 1.3

def estimate_corners(team):
    return 5.5

# =========================
# UI: SELECTORES
# =========================
leagues = get_matches()

if not leagues:
    st.warning("No hay partidos 😢")
    st.stop()

selected_league = st.selectbox("🏆 Liga", list(leagues.keys()))
matches = leagues[selected_league]

selected_match = st.selectbox("📅 Partido", list(matches.keys()))
data = matches[selected_match]

# =========================
# CARD PARTIDO
# =========================
st.markdown(f"""
<div class="card">
    <h2>{data['home']} 🆚 {data['away']}</h2>
    <p>{data['league']}</p>
</div>
""", unsafe_allow_html=True)

# =========================
# BOTÓN
# =========================
calculate = st.button("🚀 Analizar Partido")

# =========================
# SIMULACIÓN
# =========================
if calculate:

    loader = st.empty()
    loader.markdown('<div class="center"><div class="loader"></div></div>', unsafe_allow_html=True)

    time.sleep(1)

    xg_home = estimate_xg(data["home"])
    xg_away = estimate_xg(data["away"])

    corners_home = estimate_corners(data["home"])
    corners_away = estimate_corners(data["away"])

    N = 10000

    # 🔥 distribución mejorada
    xg_home_sim = np.random.gamma(2.0, xg_home / 2.0, N)
    xg_away_sim = np.random.gamma(2.0, xg_away / 2.0, N)

    home_goals = np.random.poisson(xg_home_sim)
    away_goals = np.random.poisson(xg_away_sim)

    home_win = np.mean(home_goals > away_goals)
    draw = np.mean(home_goals == away_goals)
    away_win = np.mean(home_goals < away_goals)

    total_goals = home_goals + away_goals
    btts = np.mean((home_goals > 0) & (away_goals > 0))

    home_c = np.random.poisson(corners_home, N)
    away_c = np.random.poisson(corners_away, N)
    total_c = home_c + away_c

    loader.empty()

    # =========================
    # PICKS
    # =========================
    st.header("🔥 Picks del Partido")

    if home_win > 0.60:
        st.markdown('<div class="pick good">✅ Gana Local</div>', unsafe_allow_html=True)

    if away_win > 0.60:
        st.markdown('<div class="pick good">✅ Gana Visitante</div>', unsafe_allow_html=True)

    if btts > 0.65:
        st.markdown('<div class="pick good">✅ BTTS Sí</div>', unsafe_allow_html=True)

    if np.mean(total_goals > 2.5) > 0.65:
        st.markdown('<div class="pick good">✅ Over 2.5 goles</div>', unsafe_allow_html=True)

    # =========================
    # PROBABILIDADES
    # =========================
    st.header("📊 Probabilidades 1X2")

    col1, col2, col3 = st.columns(3)

    col1.metric("🏠 Local", f"{home_win:.2%}")
    col2.metric("🤝 Empate", f"{draw:.2%}")
    col3.metric("✈️ Visitante", f"{away_win:.2%}")

    # =========================
    # DASHBOARD
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚽ Goles")
        for line in [1.5, 2.5, 3.5]:
            prob = np.mean(total_goals > line)
            st.write(f"Más de {line}: {prob:.2%}")

        st.subheader("🎯 BTTS")
        st.write(f"Sí: {btts:.2%}")
        st.write(f"No: {(1 - btts):.2%}")

    with col2:
        st.subheader("🚩 Córners")
        st.write(f"Promedio: {np.mean(total_c):.2f}")

        for line in [8.5, 9.5, 10.5]:
            prob = np.mean(total_c > line)
            st.write(f"Más de {line}: {prob:.2%}")