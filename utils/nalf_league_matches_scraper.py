from utils.scraper import Scraper


class NALFleagueMatchesScraper(Scraper):
    def __init__(self, link):
        self.url = f'http://nalffutsal.pl/?page_id={link}'
        super().__init__(self.url)

    def scrape_matches(self):
        content = self.scrape_content()
        matches_list = content['table']
        division = content['title']
        data_objects_list = []

        # Iteruj przez każdy wiersz
        for idx, match in enumerate(matches_list):
            teams = self.get_teams(match.find_all('a')[1].text)
            if teams is None:
                continue
            scores = self.get_match_result(match.find_all('a')[2].text)
            data_object = {
                "team1": teams[0],
                "team2": teams[1],
                "score1": scores[0],
                "score2": scores[1],
                "competitions": 1,
                "division": self.get_division_name_from_title(division),
                "date": match.find_all('date')[0].text,
                "event_id": self.get_event_id(match.find_all('a')[2].get('href'))
            }

            # Dodaj obiekt do listy
            data_objects_list.append(data_object)

        # Możesz zwrócić listę obiektów lub dalej przetwarzać dane
        return {'matches': data_objects_list, 'division': division}

    def get_teams(self, _data):
        if ' — ' in _data:
            teams = _data.lstrip().split(' — ')
            return teams
        return None

    def get_match_result(self, _data):
        if ' - ' in _data:
            score_a, score_b = _data.split(' - ')
            return [int(score_a), int(score_b)]
        return [None, None]

    def get_division_name_from_title(self, division_title):
        return division_title.replace(' Terminarz', '')

    def get_event_id(self, _data):
        x = str(_data)
        y = x.split('=')[-1]
        print('scraper', y)
        return _data.split('=')[-1]


# # Przykład użycia klasy
# url_to_scrape = 'http://nalffutsal.pl/?page_id=34' # A
# # url_to_scrape = 'http://nalffutsal.pl/?page_id=52' # B
# scraper = NALFmatchesScraper(url_to_scrape)
# data_objects = scraper.scrape_matches()
#
# file_generator = JSONFileGenerator(data_objects)
# file_generator.generate_and_save_file('matches-a.json')
# # file_generator.generate_and_save_file('matches-b.json')

