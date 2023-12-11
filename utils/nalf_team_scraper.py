from utils.scraper import Scraper

class NALFteamScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    def scrape_team_players(self):
        # Lista do przechowywania obiektów z danymi
        rows = self.scrape_content()

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
                'yellowcards': int(row.find('td', class_='data-yellowcards').text),
                'redcards': int(row.find('td', class_='data-redcards').text),
                'owngoals': int(row.find('td', class_='data-owngoals').text),
                'best_five': int(row.find('td', class_='data-pitkakolejki').text),
                'best_player': int(row.find('td', class_='data-zawodnikkolejki').text),
            }
            #
            # # Dodaj obiekt do listy
            data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return data_objects_list

    def _get_is_goalkeeper(self, row):
        if row.find('td', class_='data-position').text == 'Bramkarz':
            return 1
        return 0



url_to_scrape = 'http://nalffutsal.pl/?sp_team=drug-ony'
scraper = NALFteamScraper(url_to_scrape)
data_objects = scraper.scrape_team_players()

for d in data_objects:
    print(d)