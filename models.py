from database import db


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
