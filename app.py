import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Betting Tool PRO", layout="wide")

st.title("CHACA TIPSTER")

API_KEY = st.secrets["API_KEY"]

# =========================
# 📡 OBTENER PARTIDOS (API FOOTBALL)
# =========================
@st.cache_data(ttl=1800)
def get_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    today = datetime.today().strftime('%Y-%m-%d')

    params = {
        "date": today
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        st.error(f"Error API: {response.status_code}")
        return {}

    data = response.json()

    leagues = {}

    for match in data["response"]:
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        if league not in leagues:
            leagues[league] = []

        leagues[league].append({
            "home": home,
            "away": away
        })

    return leagues


# =========================
# 🎯 PROBABILIDADES BASE
# =========================
def calculate_probs():
    import random
    home = round(random.uniform(40, 60), 1)
    draw = round(random.uniform(20, 30), 1)
    away = round(100 - home - draw, 1)
    return home, draw, away


# =========================
# UI
# =========================
leagues = get_matches()

if not leagues:
    st.error("⚠️ No hay partidos disponibles hoy")
    st.stop()

selected_league = st.selectbox(
    "Selecciona una liga",
    ["-- Elegir --"] + list(leagues.keys())
)

if selected_league == "-- Elegir --":
    st.warning("Selecciona una liga")
    st.stop()

st.subheader(f"📊 {selected_league}")

for match in leagues[selected_league]:
    home = match["home"]
    away = match["away"]

    p_home, p_draw, p_away = calculate_probs()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(f"### {home} vs {away}")

    with col2:
        c1, c2, c3 = st.columns(3)
        c1.metric("🏠", f"{p_home}%")
        c2.metric("🤝", f"{p_draw}%")
        c3.metric("✈️", f"{p_away}%")

    st.divider()