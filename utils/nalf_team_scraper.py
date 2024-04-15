from utils.scraper import Scraper

class NALFteamScraper(Scraper):
    def __init__(self, link):
        self.url = f'http://nalffutsal.pl/?sp_team={link}'
        super().__init__(self.url)

    def scrape_team_players(self):
        # Lista do przechowywania obiektów z danymi
        rows = self.scrape_content()['table']

        data_objects_list = []

        # Iteruj przez każdy wiersz
        for row in rows:
            data_object = {
                'full_name': row.find('td', class_='data-name').text,
                'link': row.find('td', class_='data-name').find('a').get('href'),
                'team': row.find('td', class_='data-team').find('a').get('href'),
                'is_goalkeeper': self._get_is_goalkeeper(row),
                'matches': int(row.find('td', class_='data-appearances').text),
                'goals': int(row.find('td', class_='data-goals').text),
                'assists': int(row.find('td', class_='data-assists').text),
                'yellow_cards': int(row.find('td', class_='data-yellowcards').text),
                'red_cards': int(row.find('td', class_='data-redcards').text),
                'own_goals': int(row.find('td', class_='data-owngoals').text),
                'best_five': int(self._get_data(row, 'data-pitkakolejki')),
                'best_player': int(self._get_data(row, 'data-zawodnikkolejki')),
            }
            #
            # # Dodaj obiekt do listy
            data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return data_objects_list


    def scrape_team_table(self):
        # Lista do przechowywania obiektów z danymi
        _content = self.scrape_content(1)
        rows = _content['table']
        team_name = _content['title']
        division = _content['division']

        data_objects_list = []

        # Iteruj przez każdy wiersz
        for row in rows:
            if row.find('a').text == team_name:
                data_object = {
                    'division': division,
                    'rank': int(row.find('td', class_='data-rank').text),
                    'team_name': row.find('a').text,
                    'matches': int(row.find('td', class_='data-m').text),
                    'wins': int(row.find('td', class_='data-z').text),
                    'draws': int(row.find('td', class_='data-r').text),
                    'losts': int(row.find('td', class_='data-p').text),
                    'goals_scored': int(row.find('td', class_='data-gz').text),
                    'goals_lost': int(row.find('td', class_='data-gs').text),
                    'points': int(row.find('td', class_='data-pkt').text),
                    'form': row.find('td', class_='data-forma').text
                }
                data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return data_objects_list


    def _get_is_goalkeeper(self, row):
        if row.find('td', class_='data-position').text == 'Bramkarz':
            return 1
        return 0

    def _get_data(self, row, classname):
        if row.find('td', class_=classname):
            return row.find('td', class_=classname).text
        return 0


# url_to_scrape = 'http://nalffutsal.pl/?sp_team=drug-ony'
# scraper = NALFteamScraper(url_to_scrape)
# data_objects = scraper.scrape_team_players()
#
# for d in data_objects:
#     print(d)