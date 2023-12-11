from utils.scraper import Scraper

class NALFtableScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    def scrape_league_table(self):
        # Lista do przechowywania obiektów z danymi
        rows = self.scrape_content()

        data_objects_list = []

        # Iteruj przez każdy wiersz
        for row in rows:
            data_object = {
                # 'rank': row.find('td', class_='data-rank').text,
                'team_name': row.find('a').text,
                'matches': int(row.find('td', class_='data-m').text),
                'wins': int(row.find('td', class_='data-m').text),
                'draws': int(row.find('td', class_='data-r').text),
                'losts': int(row.find('td', class_='data-p').text),
                'goals_scored': int(row.find('td', class_='data-gz').text),
                'goals_lost': int(row.find('td', class_='data-gs').text),
                'points': int(row.find('td', class_='data-pkt').text)
            }
            #
            # # Dodaj obiekt do listy
            data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return data_objects_list


url_to_scrape = 'http://nalffutsal.pl/?page_id=16'
scraper = NALFtableScraper(url_to_scrape)
data_objects = scraper.scrape_league_table()

print(data_objects)