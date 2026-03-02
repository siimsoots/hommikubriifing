import streamlit as st
import requests

# --- SEADISTUS JA API ---
try:
    API_KEY = st.secrets["news_api_key"]
except:
    API_KEY = '2ce3c945b7f541a99d517f2decf1528e'

st.set_page_config(page_title="Global Insight | Nutibriifing", layout="wide")

# --- CUSTOM CSS (Professionaalne ja kompaktne välimus) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stCard {
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        transition: transform 0.2s;
        height: 100%;
    }
    .stCard:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .source-label {
        color: #007bff;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
        display: block;
    }
    .news-title {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #1a1a1a !important;
        line-height: 1.3 !important;
        margin-bottom: 8px !important;
    }
    .news-desc {
        font-size: 13px !important;
        color: #555 !important;
        line-height: 1.4 !important;
    }
    img {
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KÜLGPANEEL (Sidebar) ---
st.sidebar.header("🔍 Seadista oma briifing")

# 1. Laiendatud teemad
teema_valik = st.sidebar.selectbox(
    "Vali kategooria:",
    ["Värsked maailmauudised", "Poliitika", "Julgeolek & Sõda", "Majandus & Finants", 
     "Teadus & Tehnoloogia", "Keskkond & Kliima", "Ühiskond & Kultuur", "Tervis", "Eesti fookus"]
)

# 2. Uudisteallikate valik (Maailma populaarseimad + usaldusväärsed)
allika_valik = st.sidebar.multiselect(
    "Eelistatud kanalid (valikuline):",
    options=[
        "Reuters", "BBC News", "Associated Press", "CNN", 
        "Deutsche Welle", "Al Jazeera", "Bloomberg", "The Wall Street Journal", 
        "The Guardian", "Financial Times"
    ],
    help="Kui valid konkreetsed kanalid, siis kategooria valik muutub teisejärguliseks."
)

# Kaardistame allikad NewsAPI ID-dega
source_map = {
    "Reuters": "reuters", "BBC News": "bbc-news", "Associated Press": "associated-press",
    "CNN": "cnn", "Deutsche Welle": "google-news-sa", "Al Jazeera": "al-jazeera-english",
    "Bloomberg": "bloomberg", "The Wall Street Journal": "the-wall-street-journal",
    "The Guardian": "the-guardian-uk", "Financial Times": "financial-times"
}

# --- UUDISTE HANKIMISE FUNKTSIOON ---
def fetch_news():
    base_url = "https://newsapi.org/v2/"
    params = {"apiKey": API_KEY, "pageSize": 21, "language": "en"}
    
    # Loogika: kui on valitud allikad
    if allika_valik:
        ids = [source_map[s] for s in allika_valik if s in source_map]
        params["sources"] = ",".join(ids)
        endpoint = "everything"
    else:
        # Loogika kategooriate põhjal
        endpoint = "top-headlines"
        if teema_valik == "Poliitika": params["q"] = "politics OR election"
        elif teema_valik == "Julgeolek & Sõda": endpoint = "everything"; params["q"] = "war OR military OR NATO OR security"
        elif teema_valik == "Majandus & Finants": params["category"] = "business"
        elif teema_valik == "Teadus & Tehnoloogia": params["category"] = "technology"
        elif teema_valik == "Keskkond & Kliima": endpoint = "everything"; params["q"] = "climate OR environment OR warming"
        elif teema_valik == "Ühiskond & Kultuur": endpoint = "everything"; params["q"] = "society OR culture OR human rights"
        elif teema_valik == "Tervis": params["category"] = "health"
        elif teema_valik == "Eesti fookus": endpoint = "everything"; params["q"] = "Estonia OR Tallinn"; params.pop("language")
        else: params["category"] = "general"

    try:
        r = requests.get(f"{base_url}{endpoint}", params=params)
        return r.json().get('articles', [])
    except:
        return []

# --- PEALEHT ---
st.title("☀️ Global Insight")
st.caption(f"Sinu personaalne briifing: **{teema_valik}**")

articles = fetch_news()

if not articles:
    st.info("Valitud filtritega uudiseid hetkel ei leitud. Proovi laiendada valikut.")
else:
    # 3-tulbaline vaade (kompaktsem)
    cols = st.columns(3)
    
    for idx, art in enumerate(articles):
        col = cols[idx % 3] # Jagab uudised kolme tulpa
        
        with col:
            # Uudise kasti loomine
            st.markdown(f"""
                <div class="stCard">
                    <span class="source-label">{art['source']['name']}</span>
                    <div class="news-title">{art['title'][:85]}...</div>
                    <p class="news-desc">{art['description'][:120] if art['description'] else 'Sisu kokkuvõte puudub.'}...</p>
                    <a href="{art['url']}" target="_blank" style="font-size: 12px; color: #007bff; text-decoration: none; font-weight: bold;">Loe edasi →</a>
                </div>
            """, unsafe_allow_html=True)
            
            # Pildi lisamine (kui on olemas)
            if art.get('urlToImage'):
                st.image(art['urlToImage'], use_container_width=True)
            st.write("") # Väike vahe

# --- JALUS ---
st.divider()
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Andmeallikas: NewsAPI.org | Filtreeritud erapooletuse ja usaldusväärsuse põhimõttel.</p>", unsafe_allow_html=True)
