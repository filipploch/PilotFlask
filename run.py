from flask import Flask, render_template, jsonify, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hardsecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/futsal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

TEAM_A_ID = 1
TEAM_B_ID = 3


@app.route('/match')
def match():
    return render_template('match.html')


@app.route('/teams')
def teams():
    return render_template('teams.html')


@app.route('/matchdata')
def matchdata():
    team_a = Team.query.get(TEAM_A_ID)
    team_b = Team.query.get(TEAM_B_ID)
    return jsonify({'teama': {'id': team_a.id,
                                 'full_name': team_a.full_name,
                                 'short_name': team_a.short_name,
                                 'tricot': get_tricot(team_a)
                                 },
                       'teamb': {'id': team_b.id,
                                 'full_name': team_b.full_name,
                                 'short_name': team_b.short_name,
                                 'tricot': get_tricot(team_b)
                                 },
                       })


def get_tricot(team):
    if team.selected_tricot == 1:
        tricot = [team.home_color_one, team.home_color_two, team.home_color_three]
    else:
        tricot = [team.away_color_one, team.away_color_two, team.away_color_three]
    return tricot


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


if __name__ == '__main__':
    app.run(port=5555)
