from utils.scraper import Scraper
from utils.json_file_generator import JSONFileGenerator

class NALFmatchesScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    def scrape_matches(self):
        # Lista do przechowywania obiektów z danymi
        matches_list = self.scrape_content()

        data_objects_list = []

        # Iteruj przez każdy wiersz
        for idx, match in enumerate(matches_list):
            data_object = {
                "id": idx + 1,
                "date": match.find_all('date')[0].text,
                "teams": (match.find_all('a')[1].text).lstrip().split(' — '),
                "result": self.get_match_result(match.find_all('a')[2].text),
                "actual": False
            }

            # Dodaj obiekt do listy
            data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return data_objects_list

    def get_match_result(self, _data):
        if ' - ' in _data:
            return _data.split(' - ')
        return ''

# Przykład użycia klasy
# url_to_scrape = 'http://nalffutsal.pl/?page_id=34' # A
url_to_scrape = 'http://nalffutsal.pl/?page_id=52' # B
scraper = NALFmatchesScraper(url_to_scrape)
data_objects = scraper.scrape_matches()

file_generator = JSONFileGenerator(data_objects)
# file_generator.generate_and_save_file('matches-a.json')
file_generator.generate_and_save_file('matches-b.json')

