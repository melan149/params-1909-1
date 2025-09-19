import streamlit as st
import fitz  # PyMuPDF
import re

def extract_parameter_from_pdf(pdf_file, parameter_query, flow_type, season):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

    # Słowa kluczowe dla sezonu
    season_keywords = {
        "Winter": ["Winter", "Zima"],
        "Summer": ["Summer", "Lato"]
    }

    # Indeks wyboru wartości: pierwsza dla Supply, druga dla Exhaust
    flow_index = {"Supply": 0, "Exhaust": 1}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Sprawdź, czy strona zawiera wybrany sezon
        if not any(sk in text for sk in season_keywords[season]):
            continue

        # Wyszukaj wszystkie wystąpienia parametru z wartością i jednostką
        pattern = rf"{parameter_query}[:\s]*([\d.,]+)\s*([a-zA-Z³/°%μ]+)?"
        matches = re.findall(pattern, text, re.IGNORECASE)

        # Wybierz wartość zgodnie z typem przepływu
        index = flow_index[flow_type]
        if index < len(matches):
            value, unit = matches[index]
            results.append((page_num + 1, f"{parameter_query}", value, unit))
        elif matches:
            # Jeśli nie ma wystarczającej liczby wartości, ale coś znaleziono
            value, unit = matches[0]
            results.append((page_num + 1, f"{parameter_query}", value, unit))
        else:
            results.append((page_num + 1, f"{parameter_query}", "Nie znaleziono", ""))

    doc.close()
    return results

# Interfejs Streamlit
st.set_page_config(page_title="PDF Parameter Finder", page_icon="📘")
st.title("📘 PDF Parameter Finder z rozróżnieniem Supply/Exhaust")

uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
parameter = st.text_input("Wpisz nazwę parametru (np. 'Input Vol. Flow')")
flow_type = st.selectbox("Wybierz typ przepływu powietrza", ["Supply", "Exhaust"])
season = st.selectbox("Wybierz sezon", ["Winter", "Summer"])

if uploaded_file and parameter and flow_type and season:
    st.info(f"Szukam parametru **{parameter}** dla **{flow_type}** w sezonie **{season}**...")
    matches = extract_parameter_from_pdf(uploaded_file, parameter, flow_type, season)

    if matches:
        st.success(f"Znaleziono {len(matches)} wystąpień:")
        for page, line, value, unit in matches:
            st.write(f"📄 Strona {page}: `{line}`")
            st.write(f"➡️ Wartość: **{value} {unit}**")
    else:
        st.warning("Nie znaleziono pasujących wyników w dokumencie.")
