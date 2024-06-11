class Match(object):
    def __init__(self, team_home_name, team_home_id,
                 team_away_name, team_away_id, goals_home, goals_away):
        self.team_home_name = team_home_name
        self.team_away_name = team_away_name
        self.team_home_id = team_home_id
        self.team_away_id = team_away_id
        self.goals_home = goals_home
        self.goals_away = goals_away
