import unittest
from .sportstypes import SPORTSTYPES
import unicodedata


class TeamPoint(object):
    """
        Data structure to hold team scores, wins, goals, etc.
    """

    def __init__(self, team_id, team_name, sports_type):
        self.team_id = team_id
        self.team_name = team_name
        self.matches = 0
        self.wins = 0
        self.defeats = 0
        self.draws = 0
        self.goalsScored = 0
        self.goalsTaken = 0
        self.goalDifference = 0
        self.points = 0
        self.goalsScoredAway = 0
        # use this in direct compare mode to count goal difference of ALL matches, not only direct competitors
        self._totalGoalDifference = 0
        self._totalGoalsScored = 0
        self.pointsScored = 0
        self.pointsTaken = 0
        self.sports_type = sports_type
        self.match_list = []
        self.adjustment_goals_scored = 0
        self.adjustment_goals_taken = 0
        self.adjustment_points_scored = 0
        self.adjustment_points_taken = 0
        self.adjustment_points = 0
        self.adjustment_wins = 0
        self.adjustment_defeats = 0
        self.penalty_points = 0

    def __repr__(self):
        teamName = self.team_name
        try:
            teamName = unicode(teamName, 'utf-8')
        except (TypeError, NameError):  # unicode is a default on python 3
            pass
        teamName = unicodedata.normalize('NFKD', teamName).encode('ASCII', 'ignore')

        if self.sports_type == SPORTSTYPES.FOOTBALL:
            return u'%s - %d - %d\r\n' % (teamName, self.points, self.goalDifference)
        elif self.sports_type == SPORTSTYPES.HANDBALL:
            return u'%s - %d:%d - %d (%d A)\r\n' % (teamName, self.pointsScored, self.pointsTaken, self.goalDifference, self.goalsScoredAway)

    def add_match(self, goalsScored, goalsTaken, rival_id = None, away_score=False):
        if rival_id:
            self.match_list.append([rival_id, goalsScored, goalsTaken, away_score])
        if goalsScored < 0:
            self.goalsScored += 0
            self.goalsTaken += 5
            self.penalty_points += 1
        else:
            self.goalsScored += goalsScored
        if goalsTaken < 0:
            self.goalsScored += 5
            self.goalsTaken += 0
        else:
            self.goalsTaken += goalsTaken

        self.matches += 1
        if goalsScored > goalsTaken:
            self.wins += 1
        elif goalsScored == goalsTaken:
            self.draws += 1
        else:
            self.defeats += 1

        if away_score:
            self.goalsScoredAway += goalsScored

        self._update_fields()

    def _update_fields(self):
        self.goalDifference = self.goalsScored - self.goalsTaken + self.adjustment_goals_scored - self.adjustment_goals_taken
        if self.sports_type == SPORTSTYPES.FOOTBALL:
            self.points = (3 * self.wins + self.draws - self.penalty_points) + self.adjustment_points
        elif self.sports_type == SPORTSTYPES.HANDBALL:
            self.points = 0
            self.pointsScored = (2 * self.wins + self.draws) + self.adjustment_points_scored
            self.pointsTaken = (2 * self.defeats + self.draws) + self.adjustment_points_taken

    def direct_compare(self, rival_ids):
        """
        :param rival_ids: Liste der Gegner Ids
        :return: TeamPoint Objekt gefiltert nach obiger Liste
        """
        newTp = TeamPoint(self.team_id, self.team_name, self.sports_type)

        #[newTp.add_match(m[1],m[2]) for m in self.match_list if m[0] in rival_ids]

        for m in self.match_list:
            if m[0] in rival_ids: newTp.add_match(m[1], m[2], away_score=m[3])
            newTp._totalGoalDifference = newTp._totalGoalDifference + m[1] - m[2]
            newTp._totalGoalsScored = newTp._totalGoalsScored + m[1]

        return newTp

    def add_adjustment_football(self, goalsScored, goalsTaken, points):
        assert(self.sports_type == SPORTSTYPES.FOOTBALL)
        self.adjustment_points += points;
        self.adjustment_goals_scored += goalsScored
        self.adjustment_goals_taken += goalsTaken
        self._update_fields()

    def add_adjustment_handball(self, goalsScored, goalsTaken, pointsScored, pointsTaken, countAs):
        assert(self.sports_type == SPORTSTYPES.HANDBALL)
        self.adjustment_goals_scored += goalsScored
        self.adjustment_goals_taken += goalsTaken
        self.adjustment_points_scored += pointsScored
        self.adjustment_points_taken += pointsTaken
        if countAs == 1:
            self.adjustment_wins += 1
        elif countAs == 2:
            self.adjustment_defeats += 1
        self._update_fields()

class TeamPointTests(unittest.TestCase):
    def testSoccer1(self):
        tp = TeamPoint(89, 'Team 89', SPORTSTYPES.FOOTBALL)
        tp.add_match(3,1)
        self.assertEqual(tp.wins,1,'Number of wins not correct')
        self.assertEqual(tp.points,3,'Number of points not correct')

    def testSoccer2(self):
        tp = TeamPoint(9892, 'Team 9892', SPORTSTYPES.FOOTBALL)
        tp.add_match(0,4)
        tp.add_match(2,0)
        tp.add_match(3,3)
        tp.add_match(4,5)
        tp.add_adjustment_football(1,0,1)
        self.assertEqual(tp.wins,1,'Number of wins not correct')
        self.assertEqual(tp.points,5,'Number of points not correct')
        self.assertEqual(tp.draws,1,'Number of draws not correct')
        self.assertEqual(tp.defeats,2,'Number of defeats not correct')
        self.assertEqual(tp.goalsScored,9,'goals scored not correct')
        self.assertEqual(tp.goalsTaken,12,'goals taken not correct')
        self.assertEqual(tp.goalDifference,-2,'goal difference not correct')

    def testHandball1(self):
        tp = TeamPoint(9892, 'Team 9892', SPORTSTYPES.HANDBALL)
        tp.add_match(0,4)
        tp.add_match(2,0)
        tp.add_match(3,3)
        tp.add_match(4,5)
        self.assertEqual(tp.wins,1,'Number of wins not correct')
        self.assertEqual(tp.pointsScored,3,'Number of points scored not correct')
        self.assertEqual(tp.pointsTaken,5,'Number of points taken not correct')
        self.assertEqual(tp.draws,1,'Number of draws not correct')
        self.assertEqual(tp.defeats,2,'Number of defeats not correct')
        self.assertEqual(tp.goalsScored,9,'goals scored not correct')
        self.assertEqual(tp.goalsTaken,12,'goals taken not correct')

    def testHandball2(self):
        tp = TeamPoint(9892, 'Team 9892', SPORTSTYPES.HANDBALL)
        tp.add_match(0,4,9001)
        tp.add_match(2,0,9002)
        tp.add_match(3,3,9003)
        tp.add_match(4,5,9002)
        self.assertEqual(tp.wins,1,'Number of wins not correct')
        self.assertEqual(tp.pointsScored,3,'Number of points scored not correct')
        self.assertEqual(tp.pointsTaken,5,'Number of points taken not correct')
        self.assertEqual(tp.draws,1,'Number of draws not correct')
        self.assertEqual(tp.defeats,2,'Number of defeats not correct')
        self.assertEqual(tp.goalsScored,9,'goals scored not correct')
        self.assertEqual(tp.goalsTaken,12,'goals taken not correct')
        self.assertEqual(tp.direct_compare([9002]).goalsScored,6,'direct comparison error')
        self.assertEqual(tp.direct_compare([9001,9003]).goalsTaken,7,'direct comparison error')


def main():
    unittest.main()

if __name__ == 'main':
    main()
