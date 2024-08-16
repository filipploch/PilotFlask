import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
import json


class Scraper:

    @staticmethod
    def fetch_html(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Sprawdza, czy nie wystąpił błąd
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None

    @staticmethod
    def parse_html(html_content):
        if not html_content:
            print("HTML content is empty. Please provide valid HTML content.")
            return None
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    @staticmethod
    def get_table_header(_table):
        _table_head = _table.find('thead').find_all('tr')[1].find_all(name='th', limit=8)
        table_head = [element.text for element in _table_head]
        table_head[-1] = 'GZ'
        table_head += ['GS', '+/-']
        _table_header = {
            'rank': table_head[0],
            'team': table_head[1],
            'matches': table_head[2],
            'wins': table_head[4],
            'draws': table_head[5],
            'losses': table_head[6],
            'goals_scored': table_head[7],
            'goals_lost': table_head[8],
            'goals_difference': table_head[9],
            'points': table_head[3],
        }
        return [_table_header]

    @staticmethod
    def get_table_content(_table):
        table_content = []
        _table_rows = (_table.find('tbody').find_all('tr'))
        for row in _table_rows:
            _row = row.find_all(name='td', limit=8)
            table_row = [element.text for element in _row]
            goals_scored, goals_lost = table_row[-1].split(':')
            goals_difference = int(goals_scored) - int(goals_lost)
            table_row[-1] = goals_scored
            table_row += [goals_lost, goals_difference]
            _table_content = {
                'rank': table_row[0],
                'name': table_row[1],
                'matches': table_row[2],
                'wins': table_row[4],
                'draws': table_row[5],
                'losses': table_row[6],
                'goals_scored': table_row[7],
                'goals_lost': table_row[8],
                'goals_difference': table_row[9],
                'points': table_row[3],
            }
            table_content.append(_table_content)
        return table_content

    @staticmethod
    def get_match(row):
        game = [_game.text for _game in row.find_all(name='td')][:-1]
        game_dict = {
            'date': str(datetime.strptime(game[0], "%d.%m.%Y").date()),
            'time': str(time.fromisoformat(game[1]).strftime("%H:%M")),
            'home': game[2],
            'result': game[3].split('(')[0].strip().split(':'),
            'away': game[4],
        }
        return game_dict

    @staticmethod
    def get_schedule(soup):
        data = {}
        current_round = None

        for row in soup.select('#terminarz tr'):
            if row.find('th'):
                current_round = row.text.strip()
                data[current_round] = []
            elif row.find('td'):
                data[current_round].append(Scraper.get_match(row))
        for key in data:
            data[key] = [game for game in sorted(data[key], key=lambda x: (x['date'], x['time']))]

        return data

    @staticmethod
    def get_table(soup):
        _table = soup.find('table', {'id': 'tabela'})
        # table_header = Scraper.get_table_header(_table)
        table_content = Scraper.get_table_content(_table)
        # return table_header + table_content
        return table_content


    @staticmethod
    def get_data_from_web(url):
        soup = Scraper.parse_html(Scraper.fetch_html(url))
        table = Scraper.get_table(soup)
        schedule = Scraper.get_schedule(soup)
        return {'table': table, 'schedule': schedule}


# _data = Scraper.get_data_from_web('https://www.mzpnkrakow.pl/terminarze/2024-2025/seniorzy/v_liga_zachodnia/')
# for data in _data['table']:
#     print(data)
# print('=======================================================================================')
# print('=======================================================================================')
# for data in _data['schedule']:
#     print('=======================================================================================')
#     print(data)
#     for d in _data['schedule'][data]:
#         print(d)