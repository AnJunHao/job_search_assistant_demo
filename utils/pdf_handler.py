import fitz  # PyMuPDF

def _pdf_to_string(pdf_file) -> str: 
    pdf_stream = pdf_file.read()
    document = fitz.open(stream=pdf_stream, filetype="pdf")
    pdf_text = ""

    # acceess each page in the pdf file
    for page_num in range(document.page_count):
        page = document[page_num]
        pdf_text += page.get_text()

    return pdf_text

def pdf_to_string(file_path) -> str: 
    """Extract raw text from all pages in the PDF."""
    with fitz.open(file_path) as doc:
        raw_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            raw_text.append(page.get_text())
    return "\n".join(raw_text)