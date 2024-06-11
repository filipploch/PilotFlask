#/usr/bin/python
# coding=utf-8
from .sportstypes import SPORTSTYPES
from .match import Match
from .teampoint import TeamPoint

TABLE_ALL = 1
TABLE_HOME = 2
TABLE_AWAY = 3

CALCULATION_MODE_GOAL_DIFFERENCE = 1
CALCULATION_MODE_DIRECT_COMPARE = 2

class Standings:
    def __init__(self, table_mode=TABLE_ALL, sports_type=SPORTSTYPES.FOOTBALL, calculation_mode=1):
        self.table_items = {}
        self.table_mode = table_mode
        self.sports_type = sports_type
        self.calculation_mode = calculation_mode

    def add_adjustment_handball(self, team_id, goalsScored, goalsTaken, pointsScored, pointsTaken, countAs):
        tp = self.table_items.get(team_id)
        if tp is None:
            return
        goalsScored = int(0 if goalsScored is None else goalsScored)
        goalsTaken = int(0 if goalsTaken is None else goalsTaken)
        pointsScored = int(0 if pointsScored is None else pointsScored)
        pointsTaken = int(0 if pointsTaken is None else pointsTaken)
        tp.add_adjustment_handball(goalsScored, goalsTaken, pointsScored, pointsTaken, countAs)

    def add_adjustment_football(self, team_id, goalsScored, goalsTaken, points):
        tp = self.table_items[team_id]
        goalsScored = int(0 if goalsScored is None else goalsScored)
        goalsTaken = int(0 if goalsTaken is None else goalsTaken)
        points = int(0 if points is None else points)
        tp.add_adjustment_football(goalsScored, goalsTaken, points)

    def add_match(self, match):
        assert isinstance(match, Match)
        if match.team_home_id in self.table_items:
            tp1 = self.table_items[match.team_home_id]
        else:
            tp1 = TeamPoint(match.team_home_id, match.team_home_name, self.sports_type)
            self.table_items[match.team_home_id] = tp1

        if match.team_away_id in self.table_items:
            tp2 = self.table_items[match.team_away_id]
        else:
            tp2 = TeamPoint(match.team_away_id, match.team_away_name, self.sports_type)
            self.table_items[match.team_away_id] = tp2

        if (match.goals_home is not None and match.goals_away is not None):
            if self.table_mode != TABLE_AWAY:
                tp1.add_match(match.goals_home, match.goals_away, match.team_away_id)
            if self.table_mode != TABLE_HOME:
                tp2.add_match(match.goals_away, match.goals_home, match.team_home_id, away_score=True)

    def get_table(self):
        if (self.sports_type == SPORTSTYPES.HANDBALL):
            return self.get_table_handball()
        elif (self.sports_type == SPORTSTYPES.FOOTBALL):
            return self.get_table_fussball()

    def get_table_fussball(self):
        if self.calculation_mode == CALCULATION_MODE_DIRECT_COMPARE:
            return self.get_table_fussball_direct_compare()
        else:
            return self.get_table_fussball_normal()

    def get_table_handball(self):
        if self.calculation_mode == CALCULATION_MODE_DIRECT_COMPARE:
            return self.get_table_handball_direct_compare()
        else:
            return self.get_table_handball_normal()

    def get_table_fussball_direct_compare(self):
        tps = self.table_items.values()
        tps = sorted(tps,key=lambda x: x.points, reverse=True)
        subSortStart=0
        while subSortStart<len(tps):
            subSortEnd=subSortStart
            currentPoints = tps[subSortStart].points
            while subSortEnd < len(tps) and tps[subSortEnd].points== currentPoints:
                subSortEnd=subSortEnd+1
            if subSortEnd-subSortStart > 1:
                rival_list = [tp.team_id for tp in tps[subSortStart:subSortEnd]]
                tupleFilter = lambda x: (x.points, x.goalDifference, x._totalGoalDifference, x._totalGoalsScored)
                tps[subSortStart:subSortEnd] = sorted(tps[subSortStart:subSortEnd], key = lambda x: tupleFilter(x.direct_compare(rival_list)), reverse=True)
            subSortStart=subSortEnd
        return tps

    def get_table_fussball_normal(self):
        return sorted(self.table_items.values(), key=lambda x: (x.points, x.goalDifference, x.goalsScored),
                      reverse=True)

    def get_table_handball_normal(self):
        return sorted(self.table_items.values(), key=lambda x: (x.pointsScore, -x.pointsTaken, x.goalDifference, x.goalsScored),
                      reverse=True)

    def get_table_handball_direct_compare(self):
        tps = self.table_items.values()
        tps = sorted(tps,key=lambda x: (x.pointsScored, -x.pointsTaken), reverse=True)
        subSortStart=0
        while subSortStart<len(tps):
            subSortEnd=subSortStart
            currentPointsScored, currentPointsTaken = tps[subSortStart].pointsScored, tps[subSortStart].pointsTaken
            while subSortEnd < len(tps) and tps[subSortEnd].pointsScored == currentPointsScored and tps[subSortEnd].pointsTaken == currentPointsTaken:
                subSortEnd=subSortEnd+1
            if subSortEnd-subSortStart > 1:
                rival_list = [tp.team_id for tp in tps[subSortStart:subSortEnd]]
                tupleFilter = lambda x: (x.pointsScored, -x.pointsTaken, x.goalDifference, x.goalsScoredAway, x._totalGoalDifference)
                tps[subSortStart:subSortEnd] = sorted(tps[subSortStart:subSortEnd], key = lambda x: tupleFilter(x.direct_compare(rival_list)), reverse=True)
            subSortStart=subSortEnd
        return tps
