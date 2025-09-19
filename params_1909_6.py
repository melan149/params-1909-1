import streamlit as st
import fitz  # PyMuPDF
import re

def extract_sfp_parameter(pdf_file, flow_type):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

    # Elastyczny wzorzec dla SFP - clean filters
    pattern = r"SFP\\s*[-–]?\\s*clean\\s*filters\\s*[:\\-]?\\s*([\\d.,]+)\\s*([a-zA-Z³/°%μ]+)?"

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Znajdź wszystkie dopasowania
        matches = re.findall(pattern, text, re.IGNORECASE)

        # Wybierz wartość zgodnie z typem przepływu
        if matches:
            if flow_type == "Supply":
                value, unit = matches[0]
            elif flow_type == "Exhaust" and len(matches) > 1:
                value, unit = matches[1]
            else:
                value, unit = matches[0]
            results.append((page_num + 1, "SFP - clean filters", value, unit))

    doc.close()
    return results

# Interfejs Streamlit
st.set_page_config(page_title="SFP Parameter Finder", page_icon="📘")
st.title("📘 SFP - clean filters Finder")

uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
flow_type = st.selectbox("Wybierz typ przepływu powietrza", ["Supply", "Exhaust"])

if uploaded_file and flow_type:
    st.info(f"Szukam parametru **SFP - clean filters** dla **{flow_type}**...")
    matches = extract_sfp_parameter(uploaded_file, flow_type)

    if matches:
        st.success(f"Znaleziono {len(matches)} wystąpień:")
        for page, param, value, unit in matches:
            st.write(f"📄 Strona {page}: `{param}`")
            st.write(f"➡️ Wartość: **{value} {unit}**")
    else:
        st.warning("Nie znaleziono pasujących wyników w dokumencie.")
