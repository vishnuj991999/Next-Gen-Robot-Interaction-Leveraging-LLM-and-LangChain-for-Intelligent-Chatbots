import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_text = "".join(page.extract_text() for page in reader.pages)
    return all_text
