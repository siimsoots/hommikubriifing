import streamlit as st
import requests
from datetime import datetime

# --- SEADISTUS JA API ---
# Märkus: Kasutame sinu pakutud API võtit. 
API_KEY = '2ce3c945b7f541a99d517f2decf1528e'

st.set_page_config(page_title="Morning Briefing | Tehisintellekti Projekt", layout="wide")

# --- CUSTOM CSS (Professionaalsem ja kompaktsem välimus) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stCard {
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
        height: 420px; /* Fikseeritud kõrgus, et rivid oleksid ühtlased */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        overflow: hidden;
    }
    .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .source-label { 
        color: #d32f2f; 
        font-size: 10px; 
        font-weight: 700; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    .news-title { 
        font-size: 14px !important; 
        font-weight: 700 !important; 
        margin-top: 8px; 
        color: #1a1a1a; 
        line-height: 1.2;
        height: 50px;
        overflow: hidden;
    }
    .news-desc { 
        font-size: 12px !important; 
        color: #444 !important; 
        line-height: 1.4 !important; 
        margin-top: 10px;
        height: 80px;
        overflow: hidden;
    }
    .read-more {
        display: inline-block;
        margin-top: 10px;
        color: #0056b3;
        font-size: 12px;
        font-weight: 600;
        text-decoration: none;
    }
    img {
        border-radius: 4px;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KÜLGPANEEL (Seadistused) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2540/2540832.png", width=50)
st.sidebar.title("Seadistused")

# Kasutaja eelistused (Vaikimisi valikud)
st.sidebar.subheader("Sinu eelistused")
teema_valik = st.sidebar.selectbox(
    "Millist valdkonda soovid jälgida?",
    ["Värsked uudised", "Maailm", "Poliitika", "Julgeolek & Sõda", "Majandus", "Teadus & Tehnoloogia", "Ühiskond & Kultuur", "Keskkond"]
)

allika_valik = st.sidebar.multiselect(
    "Eelistatud kanalid (erapooletuse tagamiseks vali mitu):",
    options=["Reuters", "Associated Press", "BBC News", "Deutsche Welle", "Al Jazeera", "Bloomberg", "The Guardian", "CNN", "NBC News"],
    default=["Reuters", "BBC News", "Deutsche Welle"] # Vaikimisi valik
)

naitamise_arv = st.sidebar.slider("Uudiste arv ekraanil", 8, 40, 20)

# Uuendamise nupp
uuenda_nupp = st.sidebar.button("🔄 Värskenda briifingut", use_container_width=True)

# Allikate ID-de kaardistamine (NewsAPI toetatud allikad)
source_map = {
    "Reuters": "reuters", 
    "Associated Press": "associated-press",
    "BBC News": "bbc-news", 
    "CNN": "cnn", 
    "Deutsche Welle": "google-news-sa", 
    "Al Jazeera": "al-jazeera-english",
    "Bloomberg": "bloomberg", 
    "The Guardian": "the-guardian-uk",
    "NBC News": "nbc-news"
}

# --- UUDISTE HANKIMISE FUNKTSIOON ---
def fetch_news():
    base_url = "https://newsapi.org/v2/"
    params = {"apiKey": API_KEY, "pageSize": naitamise_arv, "language": "en"}
    
    # Kui kasutaja on valinud konkreetsed allikad
    if allika_valik:
        ids = [source_map[s] for s in allika_valik if s in source_map]
        params["sources"] = ",".join(ids)
        endpoint = "everything"
        # Kui on valitud ka teema, lisame selle otsingusõnana
        if teema_valik != "Värsked uudised":
            params["q"] = teema_valik
    else:
        # Kui allikaid pole valitud, kasutame üldist kategooriat
        endpoint = "top-headlines"
        category_map = {
            "Poliitika": "politics",
            "Majandus": "business",
            "Teadus & Tehnoloogia": "technology",
            "Keskkond": "science",
            "Ühiskond & Kultuur": "general"
        }
        
        if teema_valik in category_map:
            params["category"] = category_map[teema_valik]
        elif teema_valik == "Julgeolek & Sõda":
            endpoint = "everything"
            params["q"] = "war OR military OR NATO OR security"
        elif teema_valik == "Maailm":
            params["q"] = "world"
        else:
            params["country"] = "us"

    try:
        r = requests.get(f"{base_url}{endpoint}", params=params)
        data = r.json()
        if data.get("status") == "error":
            st.error(f"Viga uudiste pärimisel: {data.get('message')}")
            return []
        return data.get('articles', [])
    except Exception as e:
        st.error(f"Ühenduse viga: {e}")
        return []

# --- PEALEHT ---
# Tervitus vastavalt kellaajale
tund = datetime.now().hour
tervitus = "Tere hommikust!" if 5 <= tund < 12 else "Tere päevast!" if 12 <= tund < 18 else "Tere õhtust!"

st.title(f"☀️ {tervitus}")
st.subheader(f"Sinu tänane hommikubriifing: {teema_valik}")
st.info(f"Olen koondanud uudised järgmistest allikatest: {', '.join(allika_valik) if allika_valik else 'Üldised tippallikad'}. See aitab tagada erapooletu vaate.")

# Andmete laadimine
if uuenda_nupp or 'news_data' not in st.session_state:
    with st.spinner('Kogum parimatelt uudistekanalitelt infot...'):
        articles = fetch_news()
        st.session_state['news_data'] = articles
else:
    articles = st.session_state.get('news_data', [])

if not articles:
    st.warning("Valitud filtritega uudiseid ei leitud. Proovi valida teine kategooria või vähem kanaleid.")
else:
    # Kuvame uudised 4-s tulbas (kompaktsem)
    cols = st.columns(4)
    for idx, art in enumerate(articles):
        if not art.get('title') or "[Removed]" in art['title']:
            continue
            
        with cols[idx % 4]:
            # Pildi kuvamine (kui on olemas)
            image_url = art.get('urlToImage')
            if not image_url:
                image_url = "https://via.placeholder.com/300x150?text=Uudis"
            
            st.markdown(f"""
                <div class="stCard">
                    <img src="{image_url}" width="100%" height="120" style="object-fit: cover;">
                    <div style="padding-top:10px;">
                        <span class="source-label">{art['source']['name']}</span>
                        <div class="news-title">{art['title']}</div>
                        <div class="news-desc">{art['description'][:120] if art['description'] else 'Sisu nägemiseks kliki lingil...'}...</div>
                        <a href="{art['url']}" target="_blank" class="read-more">Loe täispikka artiklit →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption(f"Viimati uuendatud: {datetime.now().strftime('%H:%M:%S')} | Allikad: NewsAPI.org | Kursusetöö projekt")
