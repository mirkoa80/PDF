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
        st.error("Bitte gib eine vollständige URL ein (mit https://).")
    else:
        with st.spinner("Sammle Dateien..."):
            pdf_urls = get_all_pdfs(url_input, depth)
            
            if pdf_urls:
                st.success(f"Gefunden: {len(pdf_urls)} PDF-Dateien.")
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                    for i, pdf_url in enumerate(pdf_urls):
                        try:
                            # Dateiname säubern
                            file_name = pdf_url.split('/')[-1].split('?')[0]
                            if not file_name.lower().endswith('.pdf'):
                                file_name = f"dokument_{i}.pdf"
                            
                            # Auch beim eigentlichen Download SSL-Fehler ignorieren
                            pdf_res = requests.get(pdf_url, timeout=15, verify=False)
                            zip_file.writestr(file_name, pdf_res.content)
                        except:
                            st.warning(f"Übersprungen: {pdf_url}")
                
                st.download_button(
                    label="📥 ZIP-Archiv mit allen PDFs herunterladen",
                    data=zip_buffer.getvalue(),
                    file_name="spanisch_sammlung.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.info("Keine PDFs gefunden.")

st.divider()
st.caption("Tipp: Lade die entpackten PDFs direkt in NotebookLM hoch, um dein Spanisch-Training zu starten.")
