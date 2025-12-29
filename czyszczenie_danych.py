import numpy as np

def clear_data(df, good_year):
    # Znalezienie numeru wiersza, w którym pierwsza kolumna to "Kod stacji"
    try:
        idx_kod = df[df.iloc[:, 0] == "Kod stacji"].index[0]
    except IndexError:
        print(f"Nie znaleziono wiersza 'Kod stacji' w roku {good_year}")
        return None

    # Zapisanie kodów stacji
    code_stations = df.iloc[idx_kod, 1:].tolist()
    print(f"Liczba stacji w roku {good_year}: {len(code_stations)}")

    # Maska, w której konwertujemy dane na daty, nie-daty zamieniamy na NaT
    is_date = pd.to_datetime(df.iloc[idx_kod + 1:, 0], errors='coerce').notna()

    # Indeks pierwszego wiersza, który jest datą
    first_data_row = is_date[is_date == True].index[0]

    # Wycinamy dane właściwe od wyznaczonego dynamicznie wiersza
    df_clean = df.iloc[first_data_row:].reset_index(drop=True)

    # Oznaczenie kolumny czas i dodanie kodów stacji; konwersja na datetime
    df.columns = ['Czas'] + code_stations


    # Konwersja na datetime
    df['czas'] = pd.to_datetime(df['czas'], errors='coerce')
    df = df.dropna(subset=['czas']).reset_index(drop=True)

    df = df[df['czas'].dt.year == good_year].copy()

    # Przesunięcie pomiarów o północy na dzień poprzedni;
    mask_midnight = df['czas'].dt.hour == 0
    df.loc[mask_midnight, 'czas'] = df.loc[mask_midnight, 'czas'] - pd.Timedelta(seconds=1)

    # Sortowanie
    df = df.sort_values('czas').reset_index(drop=True)

    # Przygotowanie df do analizy danych
    df = df.melt(id_vars='czas', var_name='stacja', value_name='wartość')

    return df


def update_data(df, meta):
    # słownik klucz: stary kod, wartość: nowy kod
    code_map = {old_code.strip(): row['Kod stacji'] for _, row in meta.iterrows()
                for old_code in str(row['Stary Kod stacji \n(o ile inny od aktualnego)'] or '').split(',')
                if old_code.strip()}  # gwarancja braku pustych kluczy w słowniku

    # uaktualnienie nazw stacji w df
    df['stacja'] = df['stacja'].replace(code_map)

    return df


def add_place(df, meta):
    # słownik klucz: kod stacji, wartość: miejscowość stacji;
    place_map = dict(zip(meta['Kod stacji'], meta['Miejscowość']))

    # utworzenie kolumny 'miejscowosc' i przypisanie każdej stacji w df odpowiedniej miejscowości
    df['miejscowość'] = df['stacja'].map(place_map)

    df = df[['czas', 'stacja', 'miejscowość', 'wartość']]  # ustawienie kolejności kolumn

    return df

# Funkcja przygotowująca DateFrame do analizy (czyszczenie danych, aktualizacja kodów stacji, dodanie miejscowości)
def prepare_to_analize(df, meta, good_year):

    # Czyszczenie i niezbędne modyfikacje
    df_cleaned = clear_data(df, good_year)
    if df_cleaned is None:
        return None

    # Aktualizacja starych kodów na nowe
    df_updated = update_data(df_cleaned, meta)

    # Dodanie miejscowości i ustalenie kolejności kolumn
    df_final = add_place(df_updated, meta)

    return df_final





#Przykład jak działa update_data
"""df_test = pd.DataFrame({
    'stacja': ['001', '002', '003', '004'],
    'wartosc': [12, 15, 20, 5]
})

meta_test = pd.DataFrame({
    'Kod stacji': ['101', '102', '103'],
    'Stary Kod stacji \n(o ile inny od aktualnego)': ['001', '003,004', None]
})

print("Przed aktualizacją:")
print(df_test)

df_updated = update_data(df_test, meta_test)

print("Po aktualizacji:")
print(df_updated)"""
#001 -> 101;
#002 bez zmian (nie jest starym kodem);
#003 i 004 -> 002 (oba są starym kodami, oba zmieniają się na 002)
#103 nie ma starego kodu, ale jest też nieistotny w kontekście df_test