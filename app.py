import streamlit as st
import requests

# --- SEADISTUS ---
# Võtame API võtme seadetest (selgitan seda hiljem)
try:
    API_KEY = st.secrets["news_api_key"]
except:
    API_KEY = '2ce3c945b7f541a99d517f2decf1528e'

st.set_page_config(page_title="Nutikas Hommikubriifing", layout="wide")

# --- STIIL (CSS) ---
st.markdown("""
    <style>
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        margin-bottom: 20px;
        min-height: 380px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .source-tag {
        background-color: #ebf5ff;
        color: #007bff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    h3 { color: #1a1a1a; margin-top: 10px; font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MENÜÜ ---
st.sidebar.title("🌍 Sinu briifing")
teema = st.sidebar.selectbox("Vali valdkond:", ["Kõik", "Maailm & Poliitika", "Julgeolek & Sõda", "Teadus & Tehnoloogia", "Majandus", "Tervis"])
allikad = st.sidebar.multiselect("Eelistatud kanalid:", ["Reuters", "BBC News", "CNN", "Bloomberg", "Deutsche Welle", "Al Jazeera"])

source_map = {"Reuters": "reuters", "BBC News": "bbc-news", "CNN": "cnn", "Bloomberg": "bloomberg", "Deutsche Welle": "google-news-sa", "Al Jazeera": "al-jazeera-english"}

def fetch_data():
    base = "https://newsapi.org/v2/"
    p = {"apiKey": API_KEY, "language": "en", "pageSize": 12}
    
    if allikad:
        p["sources"] = ",".join([source_map[s] for s in allikad])
        url = base + "everything"
    else:
        url = base + "top-headlines"
        if teema == "Maailm & Poliitika": p["category"] = "general"; p["q"] = "politics"
        elif teema == "Julgeolek & Sõda": url = base + "everything"; p["q"] = "war OR military OR security"
        elif teema == "Teadus & Tehnoloogia": p["category"] = "technology"
        elif teema == "Majandus": p["category"] = "business"
        elif teema == "Tervis": p["category"] = "health"
        else: p["country"] = "us"
    
    res = requests.get(url, params=p)
    return res.json().get('articles', [])

# --- SISU ---
st.title("☀️ Nutikas Hommikubriifing")
st.write("Värskeimad uudised maailma usaldusväärsetest allikatest.")

uudised = fetch_data()

if not uudised:
    st.info("Hetkel uudiseid ei leitud. Proovi teist kategooriat.")
else:
    kolonnid = st.columns(2)
    for i, art in enumerate(uudised):
        with kolonnid[i % 2]:
            st.markdown(f"""
                <div class="stCard">
                    <span class="source-tag">{art['source']['name']}</span>
                    <h3>{art['title']}</h3>
                    <p>{art['description'][:180] if art['description'] else 'Sisu kokkuvõte puudub.'}...</p>
                    <a href="{art['url']}" target="_blank">Loe täispikka artiklit →</a>
                </div>
            """, unsafe_allow_html=True)
            if art.get('urlToImage'):
                st.image(art['urlToImage'], use_container_width=True)

st.divider()
st.caption("Allikas: NewsAPI | Loodud tehisintellekti kursuse raames.")
