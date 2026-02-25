import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import io
import zipfile

# App-Konfiguration
st.set_page_config(page_title="PDF Crawler", page_icon="🇪🇸")
st.title("📚 PDF Collector für NotebookLM")
st.info("Diese App findet PDFs auf Webseiten für dein Spanisch-Studium.")

# Eingabe
url_input = st.text_input("Webseite eingeben:", placeholder="https://www.beispiel-spanisch.de")
depth = st.radio("Wie tief suchen?", [1, 2], index=0, horizontal=True)

def get_all_pdfs(url, max_depth):
    found = set()
    to_visit = [(url, 0)]
    visited = set()
    domain = urlparse(url).netloc

    while to_visit:
        curr_url, curr_depth = to_visit.pop(0)
        if curr_depth > max_depth or curr_url in visited:
            continue
        visited.add(curr_url)

        try:
            r = requests.get(curr_url, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                link = urljoin(curr_url, a['href'])
                if link.lower().endswith('.pdf'):
                    found.add(link)
                elif urlparse(link).netloc == domain and link not in visited:
                    to_visit.append((link, curr_depth + 1))
        except:
            continue
    return found

if st.button("🚀 Suche starten"):
    if url_input:
        with st.spinner("Scanne Seite..."):
            pdfs = get_all_pdfs(url_input, depth)
            if pdfs:
                st.success(f"{len(pdfs)} PDFs gefunden!")
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                    for p_url in pdfs:
                        name = p_url.split('/')[-1]
                        content = requests.get(p_url).content
                        zip_file.writestr(name, content)
                
                st.download_button(
                    label="📥 ZIP-Archiv herunterladen",
                    data=zip_buffer.getvalue(),
                    file_name="material_sammlung.zip",
                    mime="application/zip"
                )
            else:
                st.error("Keine PDFs gefunden.")
              
