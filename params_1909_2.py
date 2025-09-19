import streamlit as st
import fitz  # PyMuPDF
import re

def extract_parameter_with_context(pdf_file, parameter_query, flow_type, season):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

    # Definicje słów kluczowych dla kontekstu
    flow_keywords = {
        "Supply": ["Supply", "Nawiew"],
        "Exhaust": ["Exhaust", "Wywiew"]
    }
    season_keywords = {
        "Winter": ["Winter", "Zima"],
        "Summer": ["Summer", "Lato"]
    }

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Sprawdź, czy strona zawiera kontekst
        if any(fk in text for fk in flow_keywords[flow_type]) and any(sk in text for sk in season_keywords[season]):
            for line in text.split('\n'):
                if parameter_query.lower() in line.lower():
                    # Wyciągnij wartość i jednostkę
                    match = re.search(rf"{parameter_query}[:\\s]*([\\d.,]+)\\s*([a-zA-Z/°%μ]+)?", line, re.IGNORECASE)
                    if match:
                        value = match.group(1)
                        unit = match.group(2) if match.group(2) else ""
                        results.append((page_num + 1, line.strip(), value, unit))
                    else:
                        results.append((page_num + 1, line.strip(), "Nie znaleziono wartości", ""))

    doc.close()
    return results

# Interfejs Streamlit
st.set_page_config(page_title="PDF Parameter Finder", page_icon="📘")
st.title("📘 PDF Parameter Finder z kontekstem")

uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
parameter = st.text_input("Wpisz nazwę parametru (np. 'Absorbed Power')")
flow_type = st.selectbox("Wybierz typ przepływu powietrza", ["Supply", "Exhaust"])
season = st.selectbox("Wybierz sezon", ["Winter", "Summer"])

if uploaded_file and parameter and flow_type and season:
    st.info(f"Szukam parametru **{parameter}** dla **{flow_type}** w sezonie **{season}**...")
    matches = extract_parameter_with_context(uploaded_file, parameter, flow_type, season)

    if matches:
        st.success(f"Znaleziono {len(matches)} wystąpień:")
        for page, line, value, unit in matches:
            st.write(f"📄 Strona {page}: `{line}`")
            st.write(f"➡️ Wartość: **{value} {unit}**")
    else:
        st.warning("Nie znaleziono pasujących wyników w dokumencie.")
