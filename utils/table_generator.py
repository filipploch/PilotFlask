import json


class TableGenerator:
    def __init__(self, division):
        self.matches = self._get_matches_from_json(f'matches-{division}.json')

    def generate_table(self, _table=None, _match_start_index=0, _divided=False, _actual=False):
        _matches = self.matches[_match_start_index:]
        if _table is not None:
            _teams = self._get_teams_from_table(_table)
        else:
            _teams = self._get_teams_from_matches(_matches)
            _table = []
            for team in _teams:
                _table.append({
                    'team_name': team, 'matches': 0, 'wins': 0, 'draws': 0, 'losts': 0, 'goals_scored': 0,
                    'goals_lost': 0, 'points': 0, 'actual': False
                })
        for idx, match in enumerate(_matches):
            print(match, flush=True)
            if not self._check_result(match) == [0, 0]:
                if not _divided:
                    if not _actual:
                        if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                            _table = self.update_table_for_both_teams(_table, match)
                    else:
                        if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                            _table = self.update_table_for_both_teams(_table, match)
                        if match['teams'][0] in _teams and match['teams'][1] in _teams and match['actual']:
                            _table = self.update_table_for_both_teams(_table, match)
                else:
                    first_match_index = int((len(_teams) * (len(_teams) - 1)) / 2)
                    print('fmi:', first_match_index, flush=True)
                    if match['id'] <= first_match_index:
                        if not _actual:
                            if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                                _table = self.update_table_for_both_teams(_table, match)
                        else:
                            if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                                _table = self.update_table_for_both_teams(_table, match)
                            if match['teams'][0] in _teams and match['teams'][1] in _teams and match['actual']:
                                _table = self.update_table_for_both_teams(_table, match)
                    else:
                        print('-------------------', flush=True)
                        _table = self._sort_table(_table, actual=_actual)
                        group_one, group_two = self.divide_table(_table)
                        _table_one = self.generate_table(_table=group_one,
                                                         _match_start_index=first_match_index,
                                                         _actual=_actual)
                        _sorted_table_one = self._sort_table(_table_one, actual=_actual)
                        _table_two = self.generate_table(_table=group_two,
                                                         _match_start_index=first_match_index,
                                                         _actual=_actual)
                        _sorted_table_two = self._sort_table(_table_two, actual=_actual)
                        return _sorted_table_one + _sorted_table_two
        sorted_table = self._sort_table(_table, actual=_actual)
        return sorted_table

    def update_table_for_both_teams(self, _tbl, _mtch):
        self.update_table(table=_tbl,
                          team=_mtch['teams'][0],
                          goals=[_mtch['result'][0], _mtch['result'][1]],
                          points=self._check_result(_mtch)[0],
                          w_d_l=self.update_w_d_l(self._check_result(_mtch))[0],
                          is_actual=self.update_actual(_mtch))
        self.update_table(table=_tbl,
                          team=_mtch['teams'][1],
                          goals=[_mtch['result'][1], _mtch['result'][0]],
                          points=self._check_result(_mtch)[1],
                          w_d_l=self.update_w_d_l(self._check_result(_mtch))[1],
                          is_actual=self.update_actual(_mtch))
        return _tbl

    def update_actual(self, _match):
        if _match['actual']:
            return True

    def divide_table(self, _table):
        if len(_table) % 2:
            if abs(_table[int(len(_table) / 2)]['points'] - _table[int((len(_table) / 2) - 1)]['points']) <= \
                    abs(_table[int((len(_table) / 2) + 1)]['points'] - _table[int(len(_table) / 2)]['points']):
                group_one = _table[:int((len(_table) / 2) + 1)]
                group_two = _table[int((len(_table) / 2) + 1):]
            else:
                group_one = _table[:int((len(_table) / 2))]
                group_two = _table[int((len(_table) / 2)):]
        else:
            group_one = _table[:(len(_table) / 2)]
            group_two = _table[(len(_table) / 2):]

        return [group_one, group_two]

    def generate_2_table(self, _table=None, _match_start_index=0, _divided=False, _actual=False):
        _matches = self.matches[_match_start_index:]
        if _table is not None:
            _teams = self._get_teams_from_table(_table)
            _tbl = []
        else:
            _teams = self._get_teams_from_matches(_matches)
            _tbl = []
        for team in _teams:
            _tbl.append({
                'team_name': team, 'matches': 0, 'wins': 0, 'draws': 0, 'losts': 0, 'goals_scored': 0,
                'goals_lost': 0, 'points': 0, 'actual': False
            })
        for match in _matches:
            if not self._check_result(match) == [0, 0]:
                if not _actual:
                    if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                        _tbl = self.update_table_for_both_teams(_tbl, match)
                else:
                    if match['teams'][0] in _teams and match['teams'][1] in _teams and not match['actual']:
                        _tbl = self.update_table_for_both_teams(_tbl, match)
                    if match['teams'][0] in _teams and match['teams'][1] in _teams and match['actual']:
                        _tbl = self.update_table_for_both_teams(_tbl, match)
        if _tbl[0]['points'] == _tbl[1]['points']:
            if _table[0]['goals_scored'] > _table[1]['goals_scored']:
                return [_table[0], _table[1]]
            elif _table[0]['goals_scored'] < _table[1]['goals_scored']:
                return [_table[1], _table[0]]
            else:
                self.check_goals(_table)
        elif _tbl[0]['points'] > _tbl[1]['points']:
            return [_table[0], _table[1]]
        else:
            return [_table[1], _table[0]]

    def check_goals(self, teams):
        pass

    def _check_result(self, match):
        if len(match['result']) == 2:
            if match['result'][0] == match['result'][1]:
                return [1, 1]
            elif int(match['result'][0]) > int(match['result'][1]):
                return [3, 0]
            return [0, 3]
        return [0, 0]

    def update_w_d_l(self, _check_result):
        if _check_result == [3, 0]:
            return [[1, 0, 0], [0, 0, 1]]
        elif _check_result == [0, 3]:
            return [[0, 0, 1], [1, 0, 0]]
        return [[0, 1, 0], [0, 1, 0]]

    def update_table(self, table, team, goals, points, w_d_l, is_actual):
        for item in table:
            if item['team_name'] == team:
                _wins = item['wins'] + int(w_d_l[0])
                _draws = item['draws'] + int(w_d_l[1])
                _losts = item['losts'] + int(w_d_l[2])
                _goals_scored = item['goals_scored'] + int(goals[0])
                _goals_lost = item['goals_lost'] + int(goals[1])
                _matches = item['matches'] + 1
                _points = item['points'] + points
                # _actual = is_actual
                item.update({
                    'team_name': team,
                    'matches': _matches,
                    'wins': _wins,
                    'draws': _draws,
                    'losts': _losts,
                    'goals_scored': _goals_scored,
                    'goals_lost': _goals_lost,
                    'points': _points,
                    'actual': is_actual
                })

    def _get_matches_from_json(self, file_name):
        try:
            with open('static/json/' + file_name, 'r') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            print(f'Error: File "{file_name}" not found.')
        except Exception as e:
            print(f'Error: {e}')

    def _get_teams_from_matches(self, matches):
        _teams = []
        for _match in matches:
            _teams.append(_match['teams'][0])
            _teams.append(_match['teams'][1])
        return set(_teams)

    def _get_teams_from_table(self, table):
        _teams = []
        for _item in table:
            _teams.append(_item['team_name'])
        return _teams

    def _sort_table(self, table, actual):
        _table = sorted(table, key=lambda x: x['points'], reverse=True)
        sorted_table = []
        for i in reversed(range(len(_table) * 9)):
            _teams_with_i_points = []
            for team in _table:
                if team['points'] == i:
                    _teams_with_i_points.append(team)
            if len(_teams_with_i_points) == 1:
                sorted_table.append(_teams_with_i_points[0])
            if len(_teams_with_i_points) == 2:
                _tms = [_team['team_name'] for _team in _teams_with_i_points]
                _tbl = self.generate_2_table(_table=_teams_with_i_points, _actual=actual)
                for team in _tbl:
                    sorted_table.append(self.get_team_table_data(team['team_name'], _tbl))
            if len(_teams_with_i_points) > 2:
                _tms = [_team['team_name'] for _team in _teams_with_i_points]
                _tbl = self.generate_table(_table=_teams_with_i_points)
                _sorted_tbl = sorted(_tbl, key=lambda x: (x['points'], (x['goals_scored'] - x['goals_lost'])),
                                     reverse=True)
                for team in _sorted_tbl:
                    sorted_table.append(team)
        return sorted_table

    def get_team_table_data(self, team_name, table):
        for data in table:
            if data['team_name'] == team_name:
                return data



