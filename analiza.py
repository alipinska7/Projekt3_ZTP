import numpy as np

#1 wersja
def combine_years(data_dict):
    """
    Łączy dane z różnych lat i zostawia tylko stacje wspólne dla wszystkich okresów.
    data_dict: słownik {rok: dataframe}
    """
    # Dodanie kolumny 'rok' do każdego df
    all_years_list = []
    for year, df in data_dict.items():
        df_copy = df.copy()
        df_copy['rok'] = year
        all_years_list.append(df_copy) #lista df-ów

    # Połączenie wszystkiego w jeden duży df
    df_combined = pd.concat(all_years_list, ignore_index=True)

    # Liczenie stacji, które są obecne w każdym z podanych lat, liczymy w ilu unikalnych latach występuje każda stacja
    year_count_per_station = df_combined.groupby('stacja')['rok'].nunique()

    total_years = len(data_dict) #liczba lat w słowniku
    common_stations = year_count_per_station[year_count_per_station == total_years].index #wybór odpowiednich stacji

    # Filtrowanie głównego df, tak żeby zostały tylko wspólne stacje
    df_final = df_combined[df_combined['stacja'].isin(common_stations)].copy()

    return df_final

#2 wersja
def combine_years2(data_dict):
    # Dodanie kolumny 'rok' do każdego df
    for rok, df in data_dict.items():
        tmp = df.copy()
        tmp['rok'] = rok
        dfs_with_year.append(tmp)

    df_all = pd.concat([df.set_index('stacja') for df in dfs_with_year], join='inner').reset_index()

    return df_all