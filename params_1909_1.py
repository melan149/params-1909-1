import streamlit as st
import fitz  # PyMuPDF

def extract_parameter_from_pdf(pdf_file, parameter_query):
    # Wczytaj plik PDF z pamięci
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    results = []

    # Przeszukaj każdą stronę
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Szukaj linii zawierających parametr
        for line in text.split('\n'):
            if parameter_query.lower() in line.lower():
                results.append((page_num + 1, line.strip()))

    doc.close()
    return results

# Interfejs Streamlit
st.set_page_config(page_title="PDF Parameter Finder", page_icon="🔍")
st.title("🔍 PDF Parameter Finder")

uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
parameter = st.text_input("Wpisz nazwę parametru do wyszukania (np. 'Absorbed Power')")

if uploaded_file and parameter:
    st.info(f"Szukam parametru **{parameter}** w pliku PDF...")
    matches = extract_parameter_from_pdf(uploaded_file, parameter)

    if matches:
        st.success(f"Znaleziono {len(matches)} wystąpień parametru **{parameter}**:")
        for page, line in matches:
            st.write(f"📄 Strona {page}: `{line}`")
    else:
        st.warning(f"Nie znaleziono parametru **{parameter}** w dokumencie.")
