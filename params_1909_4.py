import streamlit as st
import fitz  # PyMuPDF
import re

def extract_parameter_from_pdf(pdf_file, parameter_query, flow_type, season):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

    season_keywords = {
        "Winter": ["Winter", "Zima"],
        "Summer": ["Summer", "Lato"]
    }

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        page_text = page.get_text()

        if not any(sk in page_text for sk in season_keywords[season]):
            continue

        blocks.sort(key=lambda b: (b[1], b[0]))  # sort top to bottom, left to right

        for block in blocks:
            text = block[4]
            if parameter_query.lower() in text.lower():
                x0, y0, x1, y1 = block[:4]

                same_line_blocks = [b for b in blocks if abs(b[1] - y0) < 10]
                same_line_blocks.sort(key=lambda b: b[0])  # left to right

                value = ""
                unit = ""

                # Try to find value in the same block
                match = re.search(rf"{parameter_query}[:\s]*([\d.,]+)\s*([a-zA-Z/°%μ]+)?", text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    unit = match.group(2) if match.group(2) else ""
                else:
                    # Try to find value in adjacent blocks
                    for i, b in enumerate(same_line_blocks):
                        if parameter_query.lower() in b[4].lower():
                            for j in range(i + 1, len(same_line_blocks)):
                                val_match = re.search(r"([\d.,]+)\s*([a-zA-Z/°%μ]+)?", same_line_blocks[j][4])
                                if val_match:
                                    value = val_match.group(1)
                                    unit = val_match.group(2) if val_match.group(2) else ""
                                    break
                            break

                results.append((page_num + 1, text.strip(), value if value else "Nie znaleziono", unit))

    doc.close()
    return results

# Streamlit UI
st.set_page_config(page_title="PDF Parameter Finder", page_icon="📘")
st.title("📘 PDF Parameter Finder z dynamicznym wykrywaniem układu")

uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
parameter = st.text_input("Wpisz nazwę parametru (np. 'Absorbed Power')")
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
