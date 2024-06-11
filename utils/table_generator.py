from utils.standings import Standings
from utils.standings.match import Match


class TableGenerator:


    def generate_table(self, matches, regular_round_matches=None):
        table = Standings()
        if regular_round_matches:
            _m = matches
            matches = _m[:regular_round_matches]
            matches2 = _m[regular_round_matches:]
        for match in matches:
            team1_name = match[0]
            team1_id = match[1]
            team2_name = match[2]
            team2_id = match[3]
            team1_score = match[4]
            team2_score = match[5]
            table.add_match(Match(team1_name, team1_id, team2_name, team2_id, team1_score, team2_score))
        tbl = table.get_table()
        _table = []
        for i, t in enumerate(tbl, start=1):
            _table.append(
                {'rank': i,
                 'name': t.team_name,
                 'matches': t.matches,
                 'wins': t.wins,
                 'draws': t.draws,
                 'losses': t.defeats,
                 'goals_scored': t.goalsScored,
                 'goals_lost': t.goalsTaken,
                 'goals_difference': t.goalDifference,
                 'points': t.points,
                 'group': 'non-divided-group'})
        if not regular_round_matches:
            return _table
        else:
            group1 = self.divide_table(_table)[0]
            group2 = self.divide_table(_table)[1]

            table1 = self.make_table(group1, matches2)
            table2 = self.make_table(group2, matches2)

            table1 = self.update_rank(table1)
            table2 = self.update_rank(table2, len(table1)+1)


        return table1 + table2
        # return [table1, table2]

    def make_table(self, group, matches):
        group_teams = set([team['name'] for team in group])
        print(group_teams)
        table = Standings()
        if not matches:
            print('group', group)
            return group
        for match in matches:
            team1_name = match[0]
            team1_id = match[1]
            team2_name = match[2]
            team2_id = match[3]
            team1_score = match[4]
            team2_score = match[5]
            if team1_name in group_teams and team2_name in group_teams:
                table.add_match(Match(team1_name, team1_id, team2_name, team2_id, team1_score, team2_score))
        tbl = table.get_table()
        _table = []
        for i, t in enumerate(tbl, start=1):
            _table.append(
                {'rank': i,
                 'name': t.team_name,
                 'matches': t.matches,
                 'wins': t.wins,
                 'draws': t.draws,
                 'losses': t.defeats,
                 'goals_scored': t.goalsScored,
                 'goals_lost': t.goalsTaken,
                 'goals_difference': t.goalDifference,
                 'points': t.points,
                 'group': 'non-divided-group'})
        for _team in _table:
            for team in group:
                print('lllll:', team['name'], _team['name'])
                if team['name'] == _team['name']:
                    team['matches'] += _team['matches']
                    team['wins'] += _team['wins']
                    team['draws'] += _team['draws']
                    team['losses'] += _team['losses']
                    team['goals_scored'] += _team['goals_scored']
                    team['goals_lost'] += _team['goals_lost']
                    team['goals_difference'] += _team['goals_difference']
                    team['points'] += _team['points']
                    
        return group

    def divide_table(self, _table):
        group1 = _table[:5]
        group2 = _table[6:]
        if _table[5]['points'] - _table[6]['points'] < _table[4]['points'] - _table[5]['points']:
            group2.insert(0, _table[5])
        else:
            group1.append(_table[5])
        for team in group1:
            team.update({'group': 'promotion-group'})
        for team in group2:
            team.update({'group': 'demotion-group'})
        return [group1, group2]

    def update_rank(self, table, start=1):
        for i, team in enumerate(table, start=start):
            team['rank'] = i
        return table