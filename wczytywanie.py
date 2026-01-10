import pandas as pd
import requests
import zipfile
import io, os

# id archiwum dla poszczególnych lat
gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
gios_url_ids = {2015: '236', 2018: '603', 2021: '486', 2024: '582'}
gios_pm25_file = {2015: '2015_PM25_1g.xlsx', 2018: '2018_PM25_1g.xlsx', 2021: '2021_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'}


# funkcja do ściągania podanego archiwum
def download_gios_archive(year, gios_id, filename):
    # Pobranie archiwum ZIP do pamięci
    url = f"{gios_archive_url}{gios_id}"
    response = requests.get(url)
    response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj

    # Otwórz zip w pamięci

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # znajdź właściwy plik z PM2.5
        if not filename:
            print(f"Błąd: nie znaleziono {filename}.")
        else:
            # wczytaj plik do pandas
            with z.open(filename) as f:
                try:
                    df = pd.read_excel(f, header=None)
                except Exception as e:
                    print(f"Błąd przy wczytywaniu {year}: {e}")


    return df


# Zebranie wszystkich danych do słownika
def load_all_data():

    all_years_data = {}

    # pętla po latach słownika gios_url_ids
    for year in gios_url_ids.keys():
        print(f"Wczytywanie roku {year}...")

        #pobranie id i nazwy pliku
        current_id = gios_url_ids[year]
        current_file = gios_pm25_file[year]

        #wywołanie funkcji
        df = download_gios_archive(year, current_id, current_file)

        if df is not None:
            all_years_data[year] = df

    return all_years_data

# załadowywanie metadanych
def load_metadane():
    metadata_url = (
        "https://powietrze.gios.gov.pl/pjp/archives/"
        "Metadane%20oraz%20kody%20stacji%20i%20stanowisk%20pomiarowych.xlsx"
    )
    return pd.read_excel(metadata_url)


   # metadane_id = '622'
   # metadane_file = 'Metadane oraz kody stacji i stanowisk pomiarowych.xlsx'
   #  meta = download_gios_archive("Metadane", metadane_id, metadane_file)

#awaryjne: na wypadek, gdyby nie działała strona
def load_metadane2():
    return pd.read_excel("metadane.xlsx") # Upewnij się, że plik jest w folderze z projektem

