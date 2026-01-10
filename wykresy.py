import matplotlib.pyplot as plt
import seaborn as sns

#ZADANIE 2
def city_trends_plot(df, cities, years):

    for city in cities:
        for year in years:
            df_plot = df[(df['miejscowość'] == city) & (df['rok'] == year)]
            plt.plot(df_plot['miesiąc'], df_plot['średnie_PM25'],
                     marker='o', label=f"{city} {year}")

    plt.xlabel('Miesiące', fontsize=12)
    plt.ylabel('Średnia wartość PM2.5', fontsize=12)
    plt.title("Trend średnich miesięcznych wartości PM2.5")
    plt.grid()
    plt.legend()
    plt.show()


#ZADANIE 3
def heatmap_plot(df_mean_month):

    # Lista badanych miast
    cities = df_mean_month['miejscowość'].unique()

    # Tworzenie siatki
    fig, axes = plt.subplots(nrows=5, ncols=4, figsize=(30, 25))
    axes = axes.flatten()  # spłaszczenie do listy

    for ax, city in zip(axes, cities):
        m_srednie = df_mean_month[df_mean_month['miejscowość'] == city]
        h_data = (m_srednie.pivot_table(values='średnie_PM25', index='rok', columns='miesiąc').astype(float))

        sns.heatmap(h_data, cmap='rocket_r', vmin=0.0, vmax=80.0, cbar=False, ax=ax)
        ax.set_title(city)
        ax.set_xlabel('Miesiąc')
        ax.set_ylabel('Rok')

    # Dodanie odpowiedniej legendy
    cbar = fig.colorbar(axes[0].collections[0], ax=axes, orientation='vertical')
    cbar.set_label('Średnie PM2.5')

    plt.show()


#ZADANIE 4
def barplot(df_trans):
    # Wygenerowanie grupowego wykresu słupkowego dla powyższych danych
    plt.figure(figsize=(12, 9))
    sns.barplot(data=df_trans, x='miejscowość', y='ilość przekroczeń', hue='rok', width=0.8)
    plt.title("Wykres przekroczeń dobowej normy zanieczyszczeń PM2.5 dla wybranych stacji", size=20)
    plt.ylabel("Ilość wykroczeń ponad dobową normę dla danego roku", size=13)
    plt.xlabel("Stacje", size=13)
    plt.grid()
    plt.show()