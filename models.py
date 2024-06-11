from database import db

class MatchCommentator(db.Model):
    __tablename__ = 'match_commentator'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)

class MatchCameraman(db.Model):
    __tablename__ = 'match_cameraman'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)


class MatchReferee(db.Model):
    __tablename__ = 'match_referee'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.Integer)
    team_b = db.Column(db.Integer)
    score_a = db.Column(db.Integer, default=0)
    score_b = db.Column(db.Integer, default=0)
    fouls_a = db.Column(db.Integer, default=0)
    fouls_b = db.Column(db.Integer, default=0)
    actual = db.Column(db.Integer, default=0)
    match_length = db.Column(db.Integer, default=2400)
    max_fouls = db.Column(db.Integer, default=5)
    seconds = db.Column(db.Integer, default=0)
    is_timer_active = db.Column(db.Integer, default=0)
    is_timer_countdown = db.Column(db.Integer, default=2)
    stadium = db.Column(db.Integer, db.ForeignKey('stadium.id'), nullable=False)
    date = db.Column(db.String)
    commentator = db.relationship('Staff', secondary='match_commentator', backref='commentator_matches')
    cameraman = db.relationship('Staff', secondary='match_cameraman', backref='cameraman_matches')
    referee = db.relationship('Staff', secondary='match_referee', backref='referee_matches')
    competitions = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    division = db.Column(db.Integer, db.ForeignKey('division.id'), nullable=False)
    is_scoreboard_reversed = db.Column(db.Integer, default=0)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, unique=True)
    competitions = db.Column(db.Integer)
    link = db.Column(db.String)
    short_name = db.Column(db.String, unique=True)
    home_tricot_color_number = db.Column(db.Integer)
    home_color_1 = db.Column(db.String)
    home_color_2 = db.Column(db.String)
    home_color_3 = db.Column(db.String)
    color_for_ui = db.Column(db.String)
    away_color_1 = db.Column(db.String)
    away_color_2 = db.Column(db.String)
    away_color_3 = db.Column(db.String)
    selected_tricot = db.Column(db.Integer)
    bibs_color = db.Column(db.String)
    away_tricot_color_number = db.Column(db.Integer)
    logo_file = db.Column(db.String)
    penalty_points = db.Column(db.Integer)
    players = db.relationship('Player',
                              backref='teams',
                              lazy=True,
                              order_by="[desc(Player.position), Player.default_nr]")
    name_16 = db.Column(db.String, nullable=False, unique=True)


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String)
    team = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    position = db.Column(db.String)
    matches = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    yellow_cards = db.Column(db.Integer)
    red_cards = db.Column(db.Integer)
    own_goals = db.Column(db.Integer)
    best_five = db.Column(db.Integer)
    best_player = db.Column(db.Integer)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    default_nr = db.Column(db.Integer)
    squad = db.Column(db.Integer)
    is_active = db.Column(db.Integer)
    captain = db.Column(db.Integer)
    link = db.Column(db.String)


class MatchesData(db.Model):
    __tablename__ = 'matches_data'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    action_id = db.Column(db.Integer, db.ForeignKey('match_action.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    event_time = db.Column(db.Integer, nullable=True)
    player = db.relationship('Player', backref='matches_data', lazy=True)
    team = db.relationship('Team', backref='matches_data', lazy=True)
    action = db.relationship('MatchAction', backref='matches_data', lazy=True)
    actual = db.Column(db.Integer)
    is_hided = db.Column(db.Integer)
    replay_file = db.Column(db.String)


    def __init__(self, action_id, player_id, team_id, time, match_id, actual, is_hided, replay_file):
        self.action_id = action_id
        self.player_id = player_id
        self.team_id = team_id
        self.time = time
        self.match_id = match_id
        self.actual = actual
        self.is_hided = is_hided
        self.replay_file = replay_file


class MatchAction(db.Model):
    __tablename__ = 'match_action'
    id = db.Column(db.Integer, primary_key=True)
    desc_polish = db.Column(db.String)
    action_icon = db.Column(db.String)
    action = db.relationship('MatchesData', backref='match_action', lazy=True)


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


# class Cameraman(db.Model):
#     __tablename__ = 'cameraman'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String)
#     last_name = db.Column(db.String)
#
#
# class Referee(db.Model):
#     __tablename__ = 'referee'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String)
#     last_name = db.Column(db.String)





class Stadium(db.Model):
    __tablename__ = 'stadium'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)


class Competitions(db.Model):
    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Division(db.Model):
    __tablename__ = 'division'
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    name = db.Column(db.String)
    is_cup = db.Column(db.Integer, nullable=False, default=0)


class LeagueMatches(db.Model):
    __tablename__ = 'league_matches'

    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    score1 = db.Column(db.Integer)
    score2 = db.Column(db.Integer)
    competitions = db.Column(db.Integer, db.ForeignKey('competitions.id'))
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'))
    date = db.Column(db.String)
    event_id = db.Column(db.String)
    is_actual = db.Column(db.Integer)
    team1_penalty_points = db.Column(db.Integer)
    team2_penalty_points = db.Column(db.Integer)

    team1 = db.relationship('Team', foreign_keys=[team1_id], lazy=True)
    team2 = db.relationship('Team', foreign_keys=[team2_id], lazy=True)
    competitions_rel = db.relationship('Competitions', foreign_keys=[competitions])
    division = db.relationship('Division', foreign_keys=[division_id])