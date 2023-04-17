from database import db

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.Integer)
    team_b = db.Column(db.Integer)
    score_a = db.Column(db.Integer)
    score_b = db.Column(db.Integer)
    fouls_a = db.Column(db.Integer)
    fouls_b = db.Column(db.Integer)
    actual = db.Column(db.Integer)
    match_length = db.Column(db.Integer)
    max_fouls = db.Column(db.Integer)
    seconds = db.Column(db.Integer)
    is_timer_active = db.Column(db.Integer)
    is_timer_countdown = db.Column(db.Integer)
    stadium = db.Column(db.Integer, db.ForeignKey('stadium.id'), nullable=False)
    date = db.Column(db.String)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, unique=True)
    competitions = db.Column(db.Integer)
    link = db.Column(db.String)
    short_name = db.Column(db.String, unique=True)
    home_tricot_color_number = db.Column(db.Integer)
    home_color_one = db.Column(db.String)
    home_color_two = db.Column(db.String)
    home_color_three = db.Column(db.String)
    color_for_ui = db.Column(db.String)
    away_color_one = db.Column(db.String)
    away_color_two = db.Column(db.String)
    away_color_three = db.Column(db.String)
    selected_tricot = db.Column(db.Integer)
    bibs_color = db.Column(db.String)
    away_tricot_color_number = db.Column(db.Integer)
    logo_file = db.Column(db.String)
    players = db.relationship('Player',
                              backref='teams',
                              lazy=True,
                              order_by="[desc(Player.position), Player.default_nr]")


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    team = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    position = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    default_nr = db.Column(db.Integer)
    squad = db.Column(db.Integer)
    is_active = db.Column(db.Integer)
    captain = db.Column(db.Integer)


class MatchesData(db.Model):
    __tablename__ = 'matches_data'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    action_id = db.Column(db.Integer, db.ForeignKey('match_action.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    event_time = db.Column(db.Integer, nullable=True)
    player = db.relationship('Player', backref='matches_data', lazy=True)
    team = db.relationship('Team', backref='matches_data', lazy=True)
    action = db.relationship('MatchAction', backref='matches_data', lazy=True)
    actual = db.Column(db.Integer)

    def __init__(self, action_id, player_id, team_id, time, match_id, actual):
        self.action_id = action_id
        self.player_id = player_id
        self.team_id = team_id
        self.time = time
        self.match_id = match_id
        self.actual = actual


class MatchAction(db.Model):
    __tablename__ = 'match_action'
    id = db.Column(db.Integer, primary_key=True)
    desc_polish = db.Column(db.String)
    action_icon = db.Column(db.String)
    action = db.relationship('MatchesData', backref='match_action', lazy=True)


class Commentator(db.Model):
    __tablename__ = 'commentator'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class Cameraman(db.Model):
    __tablename__ = 'cameraman'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class Referee(db.Model):
    __tablename__ = 'referee'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class MatchReferee(db.Model):
    __tablename__ = 'matchreferee'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    referee_id = db.Column(db.Integer, db.ForeignKey('referee.id'))


class MatchCommentator(db.Model):
    __tablename__ = 'matchcommentator'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    commentator_id = db.Column(db.Integer, db.ForeignKey('commentator.id'))


class MatchCameraman(db.Model):
    __tablename__ = 'matchcameraman'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    commentator_id = db.Column(db.Integer, db.ForeignKey('cameraman.id'))


class Stadium(db.Model):
    __tablename__ = 'stadium'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

