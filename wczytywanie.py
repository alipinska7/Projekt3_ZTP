import pandas as pd
import requests
import zipfile
import io, os

gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"

# funkcja do ściągania podanego archiwum
def download_gios_archive(year, gios_id, filename):
    """
        Funkcja:
        1. Pobiera archiwum ZIP z bazy GIOŚ
        2. Wypakowuje wskazany plik
        3. Wczytuje ten plik do DataFrame.
        Args:
            year (int): Rok, którego dotyczą dane (używany głównie w obsłudze błędów).
            gios_id (str): Identyfikator zasobu w URL archiwum GIOŚ.
            filename (str): Dokładna nazwa pliku Excel wewnątrz archiwum ZIP do wczytania.

        Returns:
            pd.DataFrame: Dane wczytane z pliku Excel
        Raises:
            requests.exceptions.HTTPError: gdy wystąpi błąd podczas pobierania pliku.
            zipfile.BadZipFile: gdy pobrany plik nie jest poprawnym archiwum ZIP.
        """
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


def load_all_data(gios_url_ids, gios_pm25_file):
    """
    Pobiera dane PM2.5 dla wszystkich lat zdefiniowanych w słownikach `gios_url_ids` i `gios_pm25_file`.
    Funkcja:
    - Iteruje po wszystkich latach w słowniku `gios_url_ids`.
    - Pobiera dane dla każdego roku za pomocą funkcji `download_gios_archive`.
    - Zbiera wszystkie DataFrame'y do słownika: {rok: DataFrame}.
    - Wypisuje informację o wczytywaniu roku.
    Args:
        gios_url_ids (dict): Słownik {rok: ID archiwum GIOŚ}.
        gios_pm25_file (dict): Słownik {rok: nazwa pliku PM2.5}.
    Returns:
        - dict: Słownik DataFrame'ów, gdzie klucz to rok, a wartość to DataFrame z danymi PM2.5.
    """

    all_years_data = {}

    #pętla po latach z słownika gios_url_ids
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
    """
        Wczytuje metadane stacji pomiarowych PM2.5 z archiwum GIOŚ.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji, w tym kolumny:
                          'Kod stacji', 'Miejscowość', 'Stary kod stacji (o ile istnieje)'.
    """
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
    """
        Wczytuje metadane stacji PM2.5 z lokalnego pliku Excel.
        Funkcja awaryjna, gdy serwis GIOŚ jest niedostępny.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji.
    """
    return pd.read_excel("metadane.xlsx")

