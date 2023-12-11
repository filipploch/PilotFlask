import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url):
        self.url = url
        self.html_content = self._get_html_content()

    def _get_html_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching HTML content: {e}")
            return None

    def scrape_content(self, table_index=0):
        if self.html_content:
            # Utwórz obiekt BeautifulSoup
            soup = BeautifulSoup(self.html_content, 'html.parser')

            # Znajdź div o podanym id
            primary_div = soup.find('div', {'id': 'primary'})

            # Sprawdź, czy div istnieje
            if primary_div:
                # Znajdź tabelę wewnątrz diva
                tables = primary_div.find_all('tbody')

                # Sprawdź, czy istnieje tabela o podanym indeksie
                if table_index < len(tables):
                    table = tables[table_index]

                    # Znajdź wszystkie wiersze w tabeli
                    rows = table.find_all('tr')
                    return rows


                else:
                    print(f"Nie znaleziono tabeli o indeksie {table_index} w divie o id='{'primary'}'")
            else:
                print("Nie znaleziono diva o id='primary'")
        else:
            print("Brak HTML content. Sprawdź poprawność URL lub połączenie internetowe.")

    # def scrape_matches(self):
    #     # Lista do przechowywania obiektów z danymi
    #     matches_list = self.scrape_content()
    #
    #     data_objects_list = []
    #
    #     # Iteruj przez każdy wiersz
    #     for match in matches_list:
    #         data_object = {
    #             "date": match.find_all('date')[0].text,
    #             "teams": (match.find_all('a')[1].text).lstrip().split(' — '),
    #             "result": self.get_match_result(match.find_all('a')[2].text)
    #         }
    #
    #         # Dodaj obiekt do listy
    #         data_objects_list.append(data_object)
    #
    #     # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
    #     return data_objects_list
    #
    # def get_match_result(self, _data):
    #     if ' - ' in _data:
    #         return _data.split(' - ')
    #     return ''
    #
    #
    # def scrape_content(self, table_index=0):
    #     if self.html_content:
    #         # Utwórz obiekt BeautifulSoup
    #         soup = BeautifulSoup(self.html_content, 'html.parser')
    #
    #         # Znajdź div o podanym id
    #         primary_div = soup.find('div', {'id': 'primary'})
    #
    #         # Sprawdź, czy div istnieje
    #         if primary_div:
    #             # Znajdź tabelę wewnątrz diva
    #             tables = primary_div.find_all('tbody')
    #
    #             # Sprawdź, czy istnieje tabela o podanym indeksie
    #             if table_index < len(tables):
    #                 table = tables[table_index]
    #
    #                 # Znajdź wszystkie wiersze w tabeli
    #                 rows = table.find_all('tr')
    #                 return rows
    #
    #
    #             else:
    #                 print(f"Nie znaleziono tabeli o indeksie {table_index} w divie o id='{'primary'}'")
    #         else:
    #             print("Nie znaleziono diva o id='primary'")
    #     else:
    #         print("Brak HTML content. Sprawdź poprawność URL lub połączenie internetowe.")

    # def scrape_league_table(self):
    #     # Lista do przechowywania obiektów z danymi
    #     rows = self.scrape_content()
    #
    #     data_objects_list = []
    #
    #     # Iteruj przez każdy wiersz
    #     for row in rows:
    #         data_object = {
    #             # 'rank': row.find('td', class_='data-rank').text,
    #             'team_name': row.find('a').text,
    #             'matches': int(row.find('td', class_='data-m').text),
    #             'wins': int(row.find('td', class_='data-m').text),
    #             'draws': int(row.find('td', class_='data-r').text),
    #             'losts': int(row.find('td', class_='data-p').text),
    #             'goals_scored': int(row.find('td', class_='data-gz').text),
    #             'goals_lost': int(row.find('td', class_='data-gs').text),
    #             'points': int(row.find('td', class_='data-pkt').text)
    #         }
    #         #
    #         # # Dodaj obiekt do listy
    #         data_objects_list.append(data_object)
    #
    #     # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
    #     return data_objects_list



