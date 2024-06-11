#/usr/bin/python
# coding=utf-8
from .sportstypes import SPORTSTYPES
from .match import Match
from .standings import Standings, TABLE_HOME, TABLE_AWAY, TABLE_ALL, CALCULATION_MODE_DIRECT_COMPARE
import unittest
import requests

class StandingsTest(unittest.TestCase):
    def testFussball1DirectCompare(self):
        # Fussball La Liga Santander, Saison 2016/17, 38. Spieltag
        t1 = Standings(TABLE_ALL, SPORTSTYPES.FOOTBALL, CALCULATION_MODE_DIRECT_COMPARE)

        result = requests.get('https://api.deinsportplatz.de/api/v1.1/639703/matches/231/135',
                              auth=('pytctest', 'tctest18'))
        if result.status_code == 200:
            for m in result.json().get('matches'):
                t1.add_match(Match(m.get('teamHome'), m.get('fkTeam_home'),
                                        m.get('teamAway'), m.get('fkTeam_away'),
                                        m.get('goalsHome'), m.get('goalsAway')))

        tb = t1.get_table()

        self.assertEqual(tb[0].team_id, 2588)
        self.assertEqual(tb[0].points, 93)
        self.assertEqual(tb[0].goalDifference, 65)


    def testHandball1(self):
        m1 = Match('Team 11', 11, 'Team 2', 2, 22, 24)
        m2 = Match('Team 11', 11, 'Team 3', 3, 32, 29)
        m3 = Match('Team 2', 2, 'Team 3', 3, 19, 21)
        m4 = Match('Team 4', 4, 'Team 5', 5, 13, 13)
        m5 = Match('Team 4', 4, 'Team 9', 9, 13, 12)

        t1 = Standings(TABLE_ALL, SPORTSTYPES.HANDBALL, CALCULATION_MODE_DIRECT_COMPARE)
        t1.add_match(m2)
        t1.add_match(m3)
        t1.add_match(m1)
        t1.add_match(m4)
        t1.add_match(m5)

        tb = t1.get_table()
        self.assertEqual(tb[0].team_id,4)
        self.assertEqual(tb[1].team_id,11)
        self.assertEqual(tb[2].team_id,2)
        self.assertEqual(tb[3].team_id,3)

    def testHandball2(self):
        # Handball 3. Liga Herren, Saison 2015/16, 17. Spieltag
        t1 = Standings(TABLE_ALL, SPORTSTYPES.HANDBALL, CALCULATION_MODE_DIRECT_COMPARE)

        t1.add_match(Match('DHK Flensborg', 35551, 'SC Magdeburg II', 35561, 41, 23))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'TS Großburgwedel', 35661, 26, 17))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'Stralsunder HV', 35641, 20, 20))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'TSV Altenholz', 35621, 18, 25))
        t1.add_match(Match('Füchse Berlin II', 35571, 'SG Fle-Ha II', 35581, 30, 20))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'Dessau-Rosslauer HV', 35541, 25, 25))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'Oranienburger HC', 35521, 25, 22))
        t1.add_match(Match('HSV Hannover', 35591, 'VfL Potsdam', 35601, 18, 26))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'HSV Hannover', 35591, 22, 24))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'DHK Flensborg', 35551, 29, 23))
        t1.add_match(Match('Oranienburger HC', 35521, 'Eintracht Hildesheim', 35531, 29, 26))
        t1.add_match(Match('SC Magdeburg II', 35561, 'Füchse Berlin II', 35571, 41, 24))
        t1.add_match(Match('TSV Altenholz', 35621, 'SV Anhalt Bernburg', 35631, 30, 22))
        t1.add_match(Match('TS Großburgwedel', 35661, 'TSV Burgdorf II', 35511, 27, 25))
        t1.add_match(Match('Stralsunder HV', 35641, 'SV Meck.-Schwerin', 35651, 21, 24))
        t1.add_match(Match('VfL Potsdam', 35601, 'HSV Insel Usedom', 35611, 26, 25))
        t1.add_match(Match('DHK Flensborg', 35551, 'Oranienburger HC', 35521, 24, 25))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'TSV Altenholz', 35621, 24, 23))
        t1.add_match(Match('HSV Hannover', 35591, 'SC Magdeburg II', 35561, 29, 31))
        t1.add_match(Match('Füchse Berlin II', 35571, 'Dessau-Rosslauer HV', 35541, 29, 29))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'VfL Potsdam', 35601, 30, 23))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'SG Fle-Ha II', 35581, 22, 28))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'Stralsunder HV', 35641, 33, 23))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'TS Großburgwedel', 35661, 29, 29))
        t1.add_match(Match('Oranienburger HC', 35521, 'Füchse Berlin II', 35571, 32, 25))
        t1.add_match(Match('TSV Altenholz', 35621, 'TSV Burgdorf II', 35511, 25, 27))
        t1.add_match(Match('VfL Potsdam', 35601, 'SV Meck.-Schwerin', 35651, 30, 17))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'SV Anhalt Bernburg', 35631, 18, 19))
        t1.add_match(Match('SC Magdeburg II', 35561, 'HSV Insel Usedom', 35611, 33, 23))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'HSV Hannover', 35591, 35, 29))
        t1.add_match(Match('Stralsunder HV', 35641, 'Eintracht Hildesheim', 35531, 27, 29))
        t1.add_match(Match('TS Großburgwedel', 35661, 'DHK Flensborg', 35551, 27, 28))
        t1.add_match(Match('SC Magdeburg II', 35561, 'SG Fle-Ha II', 35581, 33, 27))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'Eintracht Hildesheim', 35531, 32, 20))
        t1.add_match(Match('TS Großburgwedel', 35661, 'Stralsunder HV', 35641, 27, 19))
        t1.add_match(Match('HSV Hannover', 35591, 'SV Meck.-Schwerin', 35651, 37, 25))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'SV Anhalt Bernburg', 35631, 29, 27))
        t1.add_match(Match('TSV Altenholz', 35621, 'VfL Potsdam', 35601, 30, 35))
        t1.add_match(Match('Füchse Berlin II', 35571, 'DHK Flensborg', 35551, 34, 33))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'Oranienburger HC', 35521, 29, 25))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'SC Magdeburg II', 35561, 23, 23))
        t1.add_match(Match('Füchse Berlin II', 35571, 'TS Großburgwedel', 35661, 25, 28))
        t1.add_match(Match('DHK Flensborg', 35551, 'Stralsunder HV', 35641, 23, 19))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'TSV Altenholz', 35621, 30, 27))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'SG Fle-Ha II', 35581, 24, 25))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'Dessau-Rosslauer HV', 35541, 20, 24))
        t1.add_match(Match('HSV Hannover', 35591, 'Oranienburger HC', 35521, 27, 22))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'VfL Potsdam', 35601, 28, 26))
        t1.add_match(Match('VfL Potsdam', 35601, 'Eintracht Hildesheim', 35531, 30, 25))
        t1.add_match(Match('Stralsunder HV', 35641, 'Füchse Berlin II', 35571, 30, 24))
        t1.add_match(Match('TS Großburgwedel', 35661, 'HSV Hannover', 35591, 18, 19))
        t1.add_match(Match('TSV Altenholz', 35621, 'DHK Flensborg', 35551, 27, 28))
        t1.add_match(Match('SC Magdeburg II', 35561, 'SV Meck.-Schwerin', 35651, 28, 21))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'SV Anhalt Bernburg', 35631, 25, 23))
        t1.add_match(Match('Oranienburger HC', 35521, 'HSV Insel Usedom', 35611, 35, 26))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'TSV Burgdorf II', 35511, 34, 28))
        t1.add_match(Match('HSV Hannover', 35591, 'Stralsunder HV', 35641, 25, 28))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'Oranienburger HC', 35521, 32, 31))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'TS Großburgwedel', 35661, 27, 30))
        t1.add_match(Match('Füchse Berlin II', 35571, 'TSV Altenholz', 35621, 23, 23))
        t1.add_match(Match('DHK Flensborg', 35551, 'VfL Potsdam', 35601, 29, 33))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'SG Fle-Ha II', 35581, 35, 31))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'SC Magdeburg II', 35561, 22, 27))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'Dessau-Rosslauer HV', 35541, 21, 22))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'TSV Burgdorf II', 35511, 32, 28))
        t1.add_match(Match('SC Magdeburg II', 35561, 'Eintracht Hildesheim', 35531, 32, 29))
        t1.add_match(Match('DHK Flensborg', 35551, 'SG Fle-Ha II', 35581, 25, 22))
        t1.add_match(Match('VfL Potsdam', 35601, 'Füchse Berlin II', 35571, 36, 21))
        t1.add_match(Match('TSV Altenholz', 35621, 'HSV Hannover', 35591, 32, 29))
        t1.add_match(Match('Stralsunder HV', 35641, 'HSV Insel Usedom', 35611, 34, 27))
        t1.add_match(Match('TS Großburgwedel', 35661, 'SV Anhalt Bernburg', 35631, 26, 24))
        t1.add_match(Match('Oranienburger HC', 35521, 'SV Meck.-Schwerin', 35651, 21, 19))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'HSV Insel Usedom', 35611, 39, 28))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'TS Großburgwedel', 35661, 28, 35))
        t1.add_match(Match('DHK Flensborg', 35551, 'SV Anhalt Bernburg', 35631, 25, 29))
        t1.add_match(Match('SC Magdeburg II', 35561, 'Stralsunder HV', 35641, 24, 23))
        t1.add_match(Match('Oranienburger HC', 35521, 'VfL Potsdam', 35601, 27, 26))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'TSV Altenholz', 35621, 34, 25))
        t1.add_match(Match('Füchse Berlin II', 35571, 'SV Meck.-Schwerin', 35651, 17, 22))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'HSV Hannover', 35591, 24, 22))
        t1.add_match(Match('HSV Hannover', 35591, 'Füchse Berlin II', 35571, 32, 27))
        t1.add_match(Match('TS Großburgwedel', 35661, 'SC Magdeburg II', 35561, 27, 22))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'DHK Flensborg', 35551, 23, 34))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'Eintracht Hildesheim', 35531, 22, 22))
        t1.add_match(Match('VfL Potsdam', 35601, 'SG Fle-Ha II', 35581, 30, 39))
        t1.add_match(Match('TSV Altenholz', 35621, 'Oranienburger HC', 35521, 28, 20))
        t1.add_match(Match('Stralsunder HV', 35641, 'Dessau-Rosslauer HV', 35541, 27, 25))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'TSV Burgdorf II', 35511, 29, 29))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'TSV Altenholz', 35621, 31, 27))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'TS Großburgwedel', 35661, 30, 23))
        t1.add_match(Match('DHK Flensborg', 35551, 'HSV Hannover', 35591, 37, 27))
        t1.add_match(Match('Oranienburger HC', 35521, 'Stralsunder HV', 35641, 27, 26))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'SV Anhalt Bernburg', 35631, 25, 23))
        t1.add_match(Match('SC Magdeburg II', 35561, 'VfL Potsdam', 35601, 36, 31))
        t1.add_match(Match('Füchse Berlin II', 35571, 'HSV Insel Usedom', 35611, 28, 27))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'SV Meck.-Schwerin', 35651, 30, 20))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'DHK Flensborg', 35551, 28, 32))
        t1.add_match(Match('VfL Potsdam', 35601, 'Dessau-Rosslauer HV', 35541, 21, 20))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'Füchse Berlin II', 35571, 22, 29))
        t1.add_match(Match('TS Großburgwedel', 35661, 'Oranienburger HC', 35521, 29, 24))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'TSV Burgdorf II', 35511, 25, 22))
        t1.add_match(Match('TSV Altenholz', 35621, 'SC Magdeburg II', 35561, 28, 29))
        t1.add_match(Match('Stralsunder HV', 35641, 'SG Fle-Ha II', 35581, 24, 34))
        t1.add_match(Match('HSV Hannover', 35591, 'Eintracht Hildesheim', 35531, 24, 22))
        t1.add_match(Match('HSV Insel Usedom', 35611, 'HSV Hannover', 35591, 21, 25))
        t1.add_match(Match('SV Anhalt Bernburg', 35631, 'SV Meck.-Schwerin', 35651, 25, 21))
        t1.add_match(Match('Füchse Berlin II', 35571, 'Eintracht Hildesheim', 35531, 26, 32))
        t1.add_match(Match('DHK Flensborg', 35551, 'TSV Burgdorf II', 35511, 32, 30))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'SG Fle-Ha II', 35581, 31, 29))
        t1.add_match(Match('Oranienburger HC', 35521, 'SC Magdeburg II', 35561, 24, 22))
        t1.add_match(Match('VfL Potsdam', 35601, 'Stralsunder HV', 35641, 35, 25))
        t1.add_match(Match('TSV Altenholz', 35621, 'TS Großburgwedel', 35661, 35, 26))
        t1.add_match(Match('TS Großburgwedel', 35661, 'VfL Potsdam', 35601, 26, 29))
        t1.add_match(Match('Stralsunder HV', 35641, 'TSV Altenholz', 35621, 28, 31))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'Oranienburger HC', 35521, 28, 19))
        t1.add_match(Match('SC Magdeburg II', 35561, 'Dessau-Rosslauer HV', 35541, 31, 32))
        t1.add_match(Match('Eintracht Hildesheim', 35531, 'DHK Flensborg', 35551, 26, 26))
        t1.add_match(Match('TSV Burgdorf II', 35511, 'Füchse Berlin II', 35571, 24, 20))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'HSV Insel Usedom', 35611, 28, 27))
        t1.add_match(Match('HSV Hannover', 35591, 'SV Anhalt Bernburg', 35631, 27, 29))
        t1.add_match(Match('SC Magdeburg II', 35561, 'DHK Flensborg', 35551, 30, 30))
        t1.add_match(Match('TS Großburgwedel', 35661, 'SV Meck.-Schwerin', 35651, 22, 21))
        t1.add_match(Match('Stralsunder HV', 35641, 'SV Anhalt Bernburg', 35631, 27, 28))
        t1.add_match(Match('TSV Altenholz', 35621, 'HSV Insel Usedom', 35611, 34, 29))
        t1.add_match(Match('SG Fle-Ha II', 35581, 'Füchse Berlin II', 35571, 37, 30))
        t1.add_match(Match('Dessau-Rosslauer HV', 35541, 'Eintracht Hildesheim', 35531, 22, 22))
        t1.add_match(Match('Oranienburger HC', 35521, 'TSV Burgdorf II', 35511, 27, 29))
        t1.add_match(Match('VfL Potsdam', 35601, 'HSV Hannover', 35591, 31, 29))
        t1.add_match(Match('SV Meck.-Schwerin', 35651, 'Stralsunder HV', 35641, 22, 19))

        #pprint(t1.get_table())

        tb = t1.get_table()
        self.assertEqual(tb[1].team_id,35561)
        self.assertEqual(tb[2].team_id,35601)
        self.assertEqual(tb[4].team_id,35661)

def main():
    unittest.main()

if __name__ == 'main':
    main()

