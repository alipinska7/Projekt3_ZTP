import pandas as pd

def clear_data(df, year):
    # Znalezienie wiersza z kodami stacji
    try:
        idx_kod = df.index[df.eq("Kod stacji").any(axis=1)][0]
    except IndexError:
        print(f"Nie znaleziono wiersza 'Kod stacji' w roku {year}")
        return None

    # Ustawienie nagłówków kolumn
    df.columns = df.iloc[idx_kod] #przypisanie tego wiersza jako kolumny
    df = df.iloc[idx_kod + 1:].reset_index(drop=True)

    # Usuwanie wierszy, które nie zawierają daty w pierwszej kolumnie
    df = df[pd.to_datetime(df[df.columns[0]], format='mixed', errors='coerce').notna()].reset_index(drop=True)

    # Ujednolicenie nazwy kolumny czasu
    df = df.rename(columns={df.columns[0]: "czas"})

    # Konwersja na datetime
    df['czas'] = pd.to_datetime(df['czas'], format='mixed', errors='coerce')
    df = df.dropna(subset=['czas']).reset_index(drop=True)

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
def prepare_to_analize(all_data, meta):

    processed_data = {}

    # Czyszczenie i niezbędne modyfikacje
    for year, df in all_data.items():
        df_cleaned = clear_data(df, year)
        if df_cleaned is None:
            return None

        # Aktualizacja starych kodów na nowe
        df_updated = update_data(df_cleaned, meta)

        # Dodanie miejscowości i ustalenie kolejności kolumn
        df_final = add_place(df_updated, meta)

        # Dodanie DF do słownika
        processed_data[year] = df_final

    return processed_data



def combine_years(all_data):

    # Zachowanie miejscowości z dfów
    full_df = pd.concat(all_data.values())
    place_map = full_df.drop_duplicates('stacja').set_index('stacja')['miejscowość']

    dfs = []
    for year, df in all_data.items():
        # Zmiana na format szeroki (żeby join ='inner' działało)
        pivoted = df.pivot(index='czas', columns='stacja', values='wartość')
        dfs.append(pivoted)

    # Filtrowanie stacji: wszystkie te, które występują we wszystkich analizowanych latachs
    combined_wide = pd.concat(dfs, axis=0, join='inner')

    # Powrót do odpowiedniego formatu do analizy danych
    df_all = combined_wide.reset_index().melt(
        id_vars='czas',
        var_name='stacja',
        value_name='wartość'
    )

    # Dodanie kolumny miejscowość
    df_all['miejscowość'] = df_all['stacja'].map(place_map)

    # Dodanie kolumny rok
    df_all['rok'] = df_all['czas'].dt.year

    return df_all





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