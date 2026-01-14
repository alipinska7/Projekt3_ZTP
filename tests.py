import pytest
import pandas as pd
from czyszczenie_danych import clear_data

def test_clear_data():
    df = pd.DataFrame({
        0: ["coś", "Kod stacji", "2023-01-01 00:00", "2023-01-01 01:00"],
        1: ["", "ST01", 10, 12],
        2: ["", "ST02", 20, 22],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy wynik nie jest None (np. z powodu braku nazwy "Kod Stacji")
    assert result is not None

    # Sprawdzenie, czy powstały wszystkie potrzebne kolumny
    assert set(result.columns) == {"czas", "stacja", "wartość"}

    # Sprawdzenie liczby wierszy
    assert len(result) == 4

    # Sprawdzenie przesunięcia pomiarów o północy
    midnight_row = result[result["wartość"] == 10].iloc[0]
    assert midnight_row["czas"].hour == 23
    assert midnight_row["czas"].minute == 59


def test_clear_data_no_station_code():
    df = pd.DataFrame({
        0: ["2023-01-01"],
        1: [10],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy wykryto brak "Kod Stacji", czy wyjątek został podniesiony i zwrócono None
    assert result is None


def test_clear_data_removing():
    df = pd.DataFrame({
        0: ["Kod stacji", "2023-01-01 01:00", "brak daty"],
        1: ["ST01", 10, 99],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy usunięto nieprawidłowe daty
    assert len(result) == 1
    assert result.iloc[0]["wartość"] == 10

