import streamlit as st
import requests

# --- SEADISTUS JA API ---
try:
    API_KEY = st.secrets["news_api_key"]
except:
    API_KEY = '2ce3c945b7f541a99d517f2decf1528e'

st.set_page_config(page_title="Global Insight | Nutibriifing", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stCard {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        height: 100%;
    }
    .source-label { color: #007bff; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .news-title { font-size: 16px !important; font-weight: bold !important; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- KÜLGPANEEL ---
st.sidebar.header("🔍 Seadista oma briifing")

teema_valik = st.sidebar.selectbox(
    "Vali kategooria/teema:",
    ["Värsked uudised", "Poliitika", "Julgeolek & Sõda", "Majandus", "Tehnoloogia", "Keskkond", "Tervis"]
)

allika_valik = st.sidebar.multiselect(
    "Eelistatud kanalid (valikuline):",
    options=["Reuters", "BBC News", "CNN", "Deutsche Welle", "Al Jazeera", "Bloomberg", "The Guardian"]
)

# NUPP VALIKUTE RAKENDAMISEKS
uuenda_nupp = st.sidebar.button("🚀 Uuenda briifingut", use_container_width=True)

# Allikate ID-de kaardistamine
source_map = {
    "Reuters": "reuters", "BBC News": "bbc-news", "CNN": "cnn", 
    "Deutsche Welle": "google-news-sa", "Al Jazeera": "al-jazeera-english",
    "Bloomberg": "bloomberg", "The Guardian": "the-guardian-uk"
}

# --- UUDISTE HANKIMISE FUNKTSIOON ---
def fetch_news():
    base_url = "https://newsapi.org/v2/"
    params = {"apiKey": API_KEY, "pageSize": 15, "language": "en"}
    
    # Kui on valitud allikad, kasutame "everything" endpointi, et saaks ka märksõnaga otsida
    if allika_valik:
        ids = [source_map[s] for s in allika_valik]
        params["sources"] = ",".join(ids)
        endpoint = "everything"
        # Kui teema pole "Värsked uudised", lisame selle märksõnaks
        if teema_valik != "Värsked uudised":
            params["q"] = teema_valik
    else:
        # Kui allikaid pole valitud, kasutame "top-headlines" kategooriaid
        endpoint = "top-headlines"
        if teema_valik == "Poliitika": params["category"] = "general"; params["q"] = "politics"
        elif teema_valik == "Julgeolek & Sõda": endpoint = "everything"; params["q"] = "military OR war OR NATO"
        elif teema_valik == "Majandus": params["category"] = "business"
        elif teema_valik == "Tehnoloogia": params["category"] = "technology"
        elif teema_valik == "Keskkond": endpoint = "everything"; params["q"] = "climate OR environment"
        elif teema_valik == "Tervis": params["category"] = "health"
        else: params["country"] = "us" # Vaikimisi USA tipud

    try:
        r = requests.get(f"{base_url}{endpoint}", params=params)
        data = r.json()
        if data.get("status") == "error":
            st.error(f"API viga: {data.get('message')}")
            return []
        return data.get('articles', [])
    except Exception as e:
        st.error(f"Ühenduse viga: {e}")
        return []

# --- PEALEHT ---
st.title("☀️ Global Insight")
st.caption("Sinu hommikune ülevaade maailmast.")

# Käivitame otsingu kas nupuvajutusel või esimest korda laadides
if uuenda_nupp or '
