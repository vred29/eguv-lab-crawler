from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve

def download_files(url, download_path):
    # Verificăm dacă folderul pentru descărcări există, altfel îl creăm
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Interogăm pagina web
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Căutăm toate linkurile care conțin "app/webroot/uploads/files/" și au extensia .xls
    links = soup.find_all('a', href=lambda href: href and 'app/webroot/uploads/files/' in href and href.endswith('.xls'))

    # Descărcăm fiecare fișier găsit
    for link in links:
        file_url_relative = link['href']
        file_url_absolute = urljoin(url, file_url_relative)
        file_name = file_url_absolute.split('/')[-1]

        print(f"Descărcăm: {file_name} de la adresa {file_url_absolute}")
        urlretrieve(file_url_absolute, os.path.join(download_path, file_name))
        print(f"Descărcare completă pentru: {file_name}")


if __name__ == "__main__":
    # Obținem locația curentă a scriptului
    script_location = os.path.dirname(os.path.abspath(__file__))

    # Setăm download_path pentru a fi subdirectorul "paps" în locația curentă
    url = "http://www.mmediu.ro/categorie/programul-anual-al-achizitiilor-publice/167"
    download_path = os.path.join(script_location, "paps")

    download_files(url, download_path)
