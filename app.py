import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Betting Tool PRO", layout="wide")

st.title("CHACA TIPSTER")

# 🔐 API KEY desde secrets
API_KEY = st.secrets["API_KEY"]

# =========================
# 📡 OBTENER PARTIDOS
# =========================
@st.cache_data(ttl=1800)
def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    params = {
        "dateFrom": datetime.today().strftime('%Y-%m-%d'),
        "dateTo": (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
        "competitions": "PL,PD,SA,BL1,FL1,CL"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {}

    data = response.json()

    leagues = {}

    for match in data.get("matches", []):
        league = match["competition"]["name"]
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        if league not in leagues:
            leagues[league] = []

        leagues[league].append({
            "home": home,
            "away": away
        })

    return leagues


# =========================
# 🎯 PROBABILIDADES FAKE (BASE)
# =========================
def calculate_probs():
    import random
    home = round(random.uniform(40, 60), 1)
    draw = round(random.uniform(20, 30), 1)
    away = round(100 - home - draw, 1)
    return home, draw, away


# =========================
# 🚀 UI PRINCIPAL
# =========================

leagues = get_matches()

if not leagues:
    st.error("⚠️ No se pudieron cargar partidos (API limitada o error)")
    st.stop()

# 🔽 SELECTOR OBLIGATORIO
selected_league = st.selectbox(
    "Selecciona una liga",
    options=["-- Elegir --"] + list(leagues.keys())
)

if selected_league == "-- Elegir --":
    st.warning("⚠️ Debes seleccionar una liga para ver partidos")
    st.stop()

st.subheader(f"📊 Partidos - {selected_league}")

# =========================
# 🧾 MOSTRAR PARTIDOS
# =========================
for match in leagues[selected_league]:
    home = match["home"]
    away = match["away"]

    p_home, p_draw, p_away = calculate_probs()

    with st.container():
        col1, col2 = st.columns([2, 3])

        # 🏟 Partido
        with col1:
            st.markdown(f"### {home} vs {away}")

        # 📊 Probabilidades horizontales
        with col2:
            c1, c2, c3 = st.columns(3)

            c1.metric("🏠 Local", f"{p_home}%")
            c2.metric("🤝 Empate", f"{p_draw}%")
            c3.metric("✈️ Visitante", f"{p_away}%")

    st.divider()