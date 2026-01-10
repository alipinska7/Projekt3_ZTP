import pandas as pd

#dodanie kolumny z miesiącem i zmienienie kolejności kolumn na bardziej czytelną
def add_month_column(df):

    df = df.copy()
    df['wartość'] = pd.to_numeric(df['wartość'].astype(str).str.replace(',', '.'), errors='coerce')
    df['miesiąc'] = df['czas'].dt.month
    df = df[['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']]

    return df

#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla konkretnych stacji i lat
def count_monthly_avg_station(df):

    monthly_avg = (df.groupby(['rok', 'stacja', 'miesiąc'])['wartość'].mean().reset_index()
    .rename(columns={'Wartość': 'Średnie miesięczne stężenie PM25'}))

    return monthly_avg

#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla konkretnych miast i danych lat
def count_monthly_avg_city(df, cities=None, years=None):

    # wybór konkretnych miast i lat z df_all
    df = df[(df['miejscowość'].isin(cities)) & (df['rok'].isin(years))].copy()

    # średnie miesięczne stężenia PM25, ale tylko dla Warszawy i Katowic w latach 2014 i 2024
    monthly_avg = (df.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
                          .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg



def filter_data(df):
    # Sprawdzenie, czy mamy dane dla konkretnych miesięcy w danym roku
    # Potrzebne do tego, by w wykresach nie pojawiły nam się pojedyncze dane z innych lat, których nie analizujemy
    months_per_year = (df.groupby('rok')['miesiąc'].nunique())
    valid_years = months_per_year[months_per_year >= 10].index  # gdy mamy dane dla więcej niż 10 miesięcy to ich używamy
    df = df[df['rok'].isin(valid_years)]

    return df

#ZADANIE 3
#wyliczenie średniej stężenia PM2.5 w każdym miesiącu, dla wszystkich miast i analizowanych lat
def count_monthly_avg_all_cities(df):

    df = filter_data(df)

    monthly_avg = (df.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
    .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg


# na tej podstawie określone zostało vmax w funkcji poniżej
# max_PM25 = monthly_avg_all_cities['średnie_PM25'].max()
# print(max_PM25)



#ZADANIE 4
def count_daily_avg(df):

    # Filtrowanie danych
    df = filter_data(df)

    # Tabela dobowych stężeń dla wszystkich stacji wynikająca z jednostkowych pomiarów.
    daily_avg = (df.groupby(['stacja', 'rok', 'miejscowość', df['czas']
        .dt.date])['wartość'].mean().reset_index() .rename(columns={'czas': 'data', 'wartość': 'pm25_dobowe'}) )

    # Tablica binarna stwierdzająca, czy zmierzone stężenia PM2.5 przekraczały dobową normę
    daily_avg['przekroczenie'] = ((daily_avg['pm25_dobowe'] > 15).astype(int))

    # Tabela sumująca ilość wykroczeń dla każdej stacji względem lat 2014, 2019 i 2024
    transgressions = (daily_avg.groupby(['stacja', 'rok', 'miejscowość'])['przekroczenie'].sum()
                   .reset_index().rename(columns={'przekroczenie': 'ilość przekroczeń'}))

    # Tabela dla roku 2024
    transgressions_2024 = transgressions[transgressions['rok'] == 2024]

    # Wyznaczenie 3 stacji o największej liczbie wykroczeń w roku 2024, i 3 o najmniejszej
    max_3 = transgressions_2024.nlargest(3, 'ilość przekroczeń')
    min_3 = transgressions_2024.nsmallest(3, 'ilość przekroczeń')

    chosen_stations = pd.concat([max_3, min_3])['stacja'].tolist()

    # Tabela wykroczeń dla wybranych stacji dla lat 2014, 2019 i 2024
    data_transgressions = transgressions[transgressions['stacja'].isin(chosen_stations)].copy()

    return data_transgressions



