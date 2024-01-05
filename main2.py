import os

import PyPDF2
import openpyxl
import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def download_pdf(pdf_url, download_path):
    try:
        # Efectuează o cerere GET, dezactivând verificarea SSL
        response = requests.get(pdf_url, verify=False, headers=headers)

        # Verificăm dacă descărcarea a fost cu succes (status code 200)
        if response.status_code == 200:
            # Extragem numele fișierului din URL
            file_name = pdf_url.split("/")[-1]

            # Creăm calea completă către fișierul local
            local_file_path = download_path + '/' + file_name

            # Deschidem și scriem conținutul în fișierul local
            with open(local_file_path, 'wb') as pdf_file:
                pdf_file.write(response.content)

            print(f"Descărcare completă pentru: {file_name}")
            return local_file_path
        else:
            print(f"Eroare la descărcare. Cod de stare: {response.status_code}")

    except requests.exceptions.SSLError as e:
        print(f"Eroare SSL: {e}")


def pdf_to_excel(pdf_path, excel_path):
    # Deschide fișierul PDF în modul citire binară
    with open(pdf_path, 'rb') as pdf_file:
        # Creează un obiect PDFReader
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Creează un nou fișier Excel
        wb = openpyxl.Workbook()
        ws = wb.active

        # Parcurge fiecare pagină din fișierul PDF
        for page_num in range(len(pdf_reader.pages)):
            # Extrage textul din pagina curentă
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Transformă textul într-o listă de rânduri
            rows = text.split('\n')

            # Scrie fiecare rând în fișierul Excel
            for row_index, row in enumerate(rows, start=1):
                ws.cell(row=row_index, column=page_num + 1, value=row)

        # Salvează fișierul Excel
        wb.save(excel_path)


def extract_pdf_urls(page_url):
    try:
        response = requests.get(page_url, headers=headers, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_urls = [a['href'] for a in soup.find_all('a', href=True) if "/web/wp-content/uploads/" in a['href'] and a['href'].endswith('.pdf')]
            return pdf_urls
        else:
            print(f"Eroare la accesarea paginii. Cod de stare: {response.status_code}")
            return []
    except requests.exceptions.SSLError as e:
        print(f"Eroare SSL: {e}")
        return []


def process_pdf_urls(pdf_urls, download_path):
    for pdf_url in pdf_urls:
        pdf_path = download_pdf(pdf_url, download_path)
        if pdf_path:
            file_name = pdf_url.split("/")[-1].replace(".pdf", ".xlsx")
            excel_path = os.path.join(download_path, file_name)
            pdf_to_excel(pdf_path, excel_path)
            print(f"Conținutul PDF a fost salvat în {excel_path}")


if __name__ == "__main__":
    script_location = os.path.dirname(os.path.abspath(__file__))
    page_url = "https://anap.gov.ro/web/rapoarte-de-evaluare-a-implementarii-legii-nr-522003/programul-anual/"
    download_path = os.path.join(script_location, "paps2")

    pdf_urls = extract_pdf_urls(page_url)
    process_pdf_urls(pdf_urls, download_path)
