import pandas as pd

#dodanie kolumny z miesiącem i zmienienie kolejności kolumn na bardziej czytelną
def add_month_column(df):
    """
        Dodaje kolumnę 'miesiąc' do DataFrame i zmienia kolejność kolumn na bardziej czytelną.
        Funkcja dodatkowo:
        - konwertuje kolumnę 'wartość' na typ numeryczny (zastępując przecinki kropkami)
        - ustawia kolumny w kolejności: ['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'czas', 'stacja', 'miejscowość', 'rok', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'miesiąc' i uporządkowanymi kolumnami.
    """

    df = df.copy()
    df['wartość'] = pd.to_numeric(df['wartość'].astype(str).str.replace(',', '.'), errors='coerce')
    df['miesiąc'] = df['czas'].dt.month
    df = df[['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']]

    return df

#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla konkretnych stacji i lat
def count_monthly_avg_station(df):
    """
        Wylicza średnie miesięczne stężenie PM2.5 dla każdej stacji i każdego roku.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'rok', 'stacja', 'miesiąc', 'wartość', 'miejscowość', 'czas'.
        Returns:
            pd.DataFrame: DataFrame z kolumnami:
                          'rok', 'stacja', 'miesiąc', 'średnie_PM25' zawierający średnie miesięczne wartości PM2.5.
    """

    monthly_avg = (df.groupby(['rok', 'stacja', 'miesiąc'])['wartość'].mean().reset_index()
    .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg

#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla konkretnych miast i danych lat
def count_monthly_avg_city(df, cities=None, years=None):
    """
        Wylicza średnie miesięczne stężenie PM2.5 dla wybranych miast i lat.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'miejscowość', 'rok', 'miesiąc', 'wartość'.
            cities (list, optional): Lista miast, dla których wyliczamy średnie. Domyślnie None (brak filtrowania).
            years (list, optional): Lista lat, dla których wyliczamy średnie. Domyślnie None (brak filtrowania).
        Returns:
            pd.DataFrame: DataFrame z kolumnami:
                          'miejscowość', 'rok', 'miesiąc', 'średnie_PM25' dla wybranych miast i lat.
    """
    # wybór konkretnych miast i lat z df_all
    df = df[(df['miejscowość'].isin(cities)) & (df['rok'].isin(years))].copy()

    # średnie miesięczne stężenia PM25, ale tylko dla określonych miast i lat
    monthly_avg = (df.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
                          .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg

#wersja 2
def count_monthly_avg_city2(df, cities=None, years=None):
    """
    Wylicza średnie miesięczne stężenie PM2.5 dla wybranych miast i lat.
    Jeśli cities lub years nie są podane, funkcja liczy dla wszystkich dostępnych.

    Args:
        df (pd.DataFrame): DataFrame z kolumnami 'miejscowość', 'rok', 'miesiąc', 'wartość'.
        cities (list, optional): Lista miast. Domyślnie None (wszystkie miasta).
        years (list, optional): Lista lat. Domyślnie None (wszystkie lata).

    Returns:
        pd.DataFrame: DataFrame z kolumnami:
                      'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
    """
    df_filtered = df.copy()

    if cities is not None:
        df_filtered = df_filtered[df_filtered['miejscowość'].isin(cities)]
    if years is not None:
        df_filtered = df_filtered[df_filtered['rok'].isin(years)]

    monthly_avg = (df_filtered.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
                   .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg




def filter_data(df):
    """
        Filtruje dane, aby zachować tylko lata, dla których mamy dane dla co najmniej 10 miesięcy.
        Funkcja jest przydatna do analizy, aby uniknąć używania lat z brakującymi danymi.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'rok' i 'miesiąc'.
        Returns:
            pd.DataFrame: Przefiltrowany DataFrame zawierający tylko lata z co najmniej 10 miesiącami danych.
    """
    # Sprawdzenie, czy mamy dane dla konkretnych miesięcy w danym roku
    # Potrzebne do tego, by w wykresach nie pojawiły nam się pojedyncze dane z innych lat, których nie analizujemy
    months_per_year = (df.groupby('rok')['miesiąc'].nunique())
    valid_years = months_per_year[months_per_year >= 10].index  # gdy mamy dane dla więcej niż 10 miesięcy to ich używamy
    df = df[df['rok'].isin(valid_years)]

    return df

#ZADANIE 3
#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla wszystkich miast i analizowanych lat
def count_monthly_avg_all_cities(df):
    """
        Wylicza średnie miesięczne stężenie PM2.5 dla wszystkich miast i analizowanych lat.
        Funkcja automatycznie filtruje lata z brakującymi danymi (<10 miesięcy) przed obliczeniem średnich.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'miejscowość', 'rok', 'miesiąc', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z kolumnami:
                          'miejscowość', 'rok', 'miesiąc', 'średnie_PM25' dla wszystkich miast i lat.
        """
    df = filter_data(df)

    monthly_avg = (df.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
    .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg


# na tej podstawie określone zostało vmax w funkcji poniżej
# max_PM25 = monthly_avg_all_cities['średnie_PM25'].max()
# print(max_PM25)



#ZADANIE 4
def count_daily_avg(df):
    """
        Oblicza średnie dobowe stężenia PM2.5, wykrywa przekroczenia normy i wybiera stacje z najwyższymi oraz najniższymi wykroczeniami.
        Funkcja:
        1. Filtruje dane, aby pozostawić tylko lata z co najmniej 10 miesiącami danych (`filter_data`).
        2. Wylicza średnie dobowe stężenia PM2.5 dla każdej stacji i roku.
        3. Tworzy kolumnę binarną `przekroczenie`, wskazującą, czy dobowa średnia przekroczyła normę 15 µg/m³.
        4. Sumuje liczbę przekroczeń dla każdej stacji w danych latach
        5. Dla roku 2024 wybiera 3 stacje z największą i 3 z najmniejszą liczbą przekroczeń.
        6. Zwraca tabelę przekroczeń dla wybranych stacji dla danych lat.

        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'stacja', 'miejscowość', 'rok', 'czas', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z liczbą przekroczeń dobowej normy PM2.5 dla wybranych stacji
                          (kolumny: 'stacja', 'rok', 'miejscowość', 'ilość przekroczeń').
        """
    # Filtrowanie danych
    df = filter_data(df)

    # Tabela dobowych stężeń dla wszystkich stacji wynikająca z jednostkowych pomiarów.
    daily_avg = (df.groupby(['stacja', 'rok', 'miejscowość', df['czas']
        .dt.date])['wartość'].mean().reset_index() .rename(columns={'czas': 'data', 'wartość': 'pm25_dobowe'}) )

    # Tablica binarna stwierdzająca, czy zmierzone stężenia PM2.5 przekraczały dobową normę
    daily_avg['przekroczenie'] = ((daily_avg['pm25_dobowe'] > 15).astype(int))

    # Tabela sumująca ilość wykroczeń dla każdej stacji względem lat danych lat
    exceedances = (daily_avg.groupby(['stacja', 'rok', 'miejscowość'])['przekroczenie'].sum()
                   .reset_index().rename(columns={'przekroczenie': 'ilość przekroczeń'}))

    # Tabela dla roku 2024
    transgressions_2024 = exceedances[exceedances['rok'] == 2024]

    # Wyznaczenie 3 stacji o największej liczbie wykroczeń w roku 2024 i 3 o najmniejszej
    max_3 = transgressions_2024.nlargest(3, 'ilość przekroczeń')
    min_3 = transgressions_2024.nsmallest(3, 'ilość przekroczeń')

    chosen_stations = pd.concat([max_3, min_3])['stacja'].tolist()

    # Tabela wykroczeń dla wybranych stacji dla danych lat
    data_exceedances = exceedances[exceedances['stacja'].isin(chosen_stations)].copy()

    return data_exceedances



