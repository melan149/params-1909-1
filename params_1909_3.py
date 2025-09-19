import streamlit as st
import fitz  # PyMuPDF
import re

def extract_parameter_with_context(pdf_file, parameter_query, flow_type, season):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

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
        blocks = page.get_text("blocks")
        page_text = page.get_text()

        if any(fk in page_text for fk in flow_keywords[flow_type]) and any(sk in page_text for sk in season_keywords[season]):
            for block in blocks:
                text = block[4]
                if parameter_query.lower() in text.lower():
                    value = ""
                    unit = ""
                    match = re.search(rf"{parameter_query}[:\s]*([\d.,]+)\s*([a-zA-Z/°%μ]+)?", text, re.IGNORECASE)
                    if match:
                        value = match.group(1)
                        unit = match.group(2) if match.group(2) else ""
                    else:
                        x0, y0, x1, y1 = block[:4]
                        for other_block in blocks:
                            ox0, oy0, ox1, oy1 = other_block[:4]
                            if abs(oy0 - y0) < 10 and ox0 > x1:
                                other_text = other_block[4]
                                val_match = re.search(r"([\d.,]+)\s*([a-zA-Z/°%μ]+)?", other_text)
                                if val_match:
                                    value = val_match.group(1)
                                    unit = val_match.group(2) if val_match.group(2) else ""
                                    break

                    results.append((page_num + 1, text.strip(), value if value else "Nie znaleziono", unit))

    doc.close()
    return results

# Streamlit UI
st.set_page_config(page_title="PDF Parameter Finder", page_icon="📘")
st.title("📘 PDF Parameter Finder z kontekstem i wartością")

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
