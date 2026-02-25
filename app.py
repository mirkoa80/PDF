import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import io
import zipfile
import urllib3

# Deaktiviert die Warnmeldungen im Log, wenn SSL-Zertifikate ignoriert werden
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- APP KONFIGURATION ---
st.set_page_config(page_title="PDF Crawler Pro", page_icon="🇪🇸", layout="centered")

st.title("📚 PDF Collector für NotebookLM")
st.markdown("""
Sammle PDF-Materialien von Webseiten ein. Diese Version ignoriert SSL-Zertifikatsfehler, 
um Abstürze bei schlecht konfigurierten Seiten (wie in deinem Log) zu vermeiden.
""")

# --- EINGABEBEREICH ---
url_input = st.text_input("Ziel-URL eingeben:", placeholder="https://www.beispiel-spanisch.de")
depth = st.select_slider("Suchtiefe (Unterseiten folgen)", options=[1, 2, 3], value=1)
start_button = st.button("🚀 Suche & Download starten", use_container_width=True)

def get_all_pdfs(start_url, max_depth):
    found_pdfs = set()
    visited_urls = set()
    to_visit = [(start_url, 0)]
    domain = urlparse(start_url).netloc

    status_text = st.empty()
    
    while to_visit:
        current_url, current_depth = to_visit.pop(0)
        
        if current_depth > max_depth or current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        status_text.text(f"🔍 Scanne: {current_url}")

        try:
            # verify=False verhindert den SSL-Absturz aus deinem Log
            response = requests.get(current_url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link_tag in soup.find_all('a', href=True):
                link = urljoin(current_url, link_tag['href'])
                
                if link.lower().endswith('.pdf'):
                    found_pdfs.add(link)
                elif urlparse(link).netloc == domain and link not in visited_urls:
                    if current_depth + 1 <= max_depth:
                        to_visit.append((link, current_depth + 1))
        except Exception as e:
            st.error(f"Fehler beim Scannen von {current_url}: {e}")
            continue
            
    status_text.empty()
    return found_pdfs

# --- HAUPTFUNKTION ---
if start_button:
    if not url_input.startswith("http"):
        st.error("Bitte gib eine vollständige URL ein (
                 
