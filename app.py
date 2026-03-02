import streamlit as st
import requests

# --- SEADISTUS JA API ---
try:
    API_KEY = st.secrets["news_api_key"]
except:
    # See on varuvariant, kui Streamlit Secrets pole seadistatud
    API_KEY = '2ce3c945b7f541a99d517f2decf1528e'

st.set_page_config(page_title="Global Insight | Nutibriifing", layout="wide")

# --- CUSTOM CSS (Kujundus) ---
st.markdown("""
    <style>
    .stCard {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        height: 100%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .source-label { color: #007bff; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .news-title { font-size: 16px !important; font-weight: bold !important; margin-top: 5px; color: #1a1a1a; }
    .news-desc { font-size: 13px !important; color: #555 !important; line-height: 1.4 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- KÜLGPANEEL (Sidebar) ---
st.sidebar.header("🔍 Seadista oma briifing")

teema_valik = st.sidebar.selectbox(
    "Vali kategooria/teema:",
    ["Värsked uudised", "Poliitika", "Julgeolek & Sõda", "Majandus", "Tehnoloogia", "Keskkond", "Tervis"]
)

allika_valik = st.sidebar.multiselect(
    "Eelistatud kanalid (valikuline):",
    options=["Reuters", "BBC News", "CNN", "Deutsche Welle", "Al Jazeera", "Bloomberg", "The Guardian"]
)

# Uuendamise nupp
uuenda_nupp = st.sidebar.button("🚀 Uuenda briifingut", use_container_width=True)

# Allikate ID-de kaardistamine NewsAPI jaoks
source_map = {
    "Reuters": "reuters", 
    "BBC News": "bbc-news", 
    "CNN": "cnn", 
    "Deutsche Welle": "google-news-sa", 
    "Al Jazeera": "al-jazeera-english",
    "Bloomberg": "bloomberg", 
    "The Guardian": "the-guardian-uk"
}

# --- UUDISTE HANKIMISE FUNKTSIOON ---
def fetch_news():
    base_url = "https://newsapi.org/v2/"
    params = {"apiKey": API_KEY, "pageSize": 18, "language": "en"}
    
    if allika_valik:
        ids = [source_map[s] for s in allika_valik if s in source_map]
        params["sources"] = ",".join(ids)
        endpoint = "everything"
        if teema_valik != "Värsked uudised":
            params["q"] = teema_valik
    else:
        endpoint = "top-headlines"
        if teema_valik == "Poliitika": params["category"] = "general"; params["q"] = "politics"
        elif teema_valik == "Julgeolek & Sõda": endpoint = "everything"; params["q"] = "military OR war OR NATO"
        elif teema_valik == "Majandus": params["category"] = "business"
        elif teema_valik == "Tehnoloogia": params["category"] = "technology"
        elif teema_valik == "Keskkond": endpoint = "everything"; params["q"] = "climate OR environment"
        elif teema_valik == "Tervis": params["category"] = "health"
        else: params["country"] = "us"

    try:
        r = requests.get(f"{base_url}{endpoint}", params=params)
        data = r.json()
        if data.get("status") == "error":
            return []
        return data.get('articles', [])
    except:
        return []

# --- PEALEHT ---
st.title("☀️ Global Insight")
st.caption("Sinu hommikune ülevaade maailmast usaldusväärsetest allikatest.")

# Loogika: kui vajutatakse nuppu VÕI kui programm laeb esimest korda
if uuenda_nupp or 'news_data' not in st.session_state:
    with st.spinner('Uuendan uudiseid...'):
        articles = fetch_news()
        st.session_state['news_data'] = articles
else:
    articles = st.session_state.get('news_data', [])

if not articles:
    st.warning("Valitud filtritega uudiseid ei leitud. Proovi valida teine kategooria või vähem kanaleid.")
else:
    # Kuvame uudised 3-s tulbas
    cols = st.columns(3)
    for idx, art in enumerate(articles):
        # Filtreerime välja tühjad või kustutatud artiklid
        if not art.get('title') or "[Removed]" in art['title']:
            continue
            
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="stCard">
                    <span class="source-label">{art['source']['name']}</span>
                    <div class="news-title">{art['title']}</div>
                    <p class="news-desc">{art['description'][:110] if art['description'] else 'Kokkuvõte puudub.'}...</p>
                    <a href="{art['url']}" target="_blank" style="color: #007bff; font-weight: bold; text-decoration: none; font-size: 13px;">Loe edasi →</a>
                </div>
            """, unsafe_allow_html=True)
            if art.get('urlToImage'):
                st.image(art['urlToImage'], use_container_width=True)

st.divider()
st.caption("Andmed: NewsAPI.org | Kasuta vasakpoolset menüüd filtrite muutmiseks.")
