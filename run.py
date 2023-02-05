from flask import Flask, render_template, jsonify, current_app, Blueprint, request
from flask_cors import CORS
from models import Team, Match
from database import db
import threading
from timer import Timer
from variables import MATCH_ID, TEAM_A_ID, TEAM_B_ID
from flask_apscheduler import APScheduler

monitor_blueprint = Blueprint('monitor', __name__)
controller_blueprint = Blueprint('controller', __name__)
timer_blueprint = Blueprint('timer', __name__)

apscheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hardsecretkey'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/futsal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(controller_blueprint)
    app.register_blueprint(timer_blueprint)
    db.init_app(app)
    apscheduler.init_app(app)
    apscheduler.start()
    timer = Timer(app)
    apscheduler.add_job(func=timer.control_timer, args=[app], id='timer')
    CORS(app)
    return app


@monitor_blueprint.route('/')
def index():
    return 'Hello World'


@timer_blueprint.route('/control-timer/<control_variable>')
def control_timer(control_variable):
    Match.query.filter_by(id=MATCH_ID).first().is_timer_active = int(control_variable)
    db.session.commit()
    return jsonify({'is_timer_active': Match.query.filter_by(id=MATCH_ID).first().is_timer_active})


@monitor_blueprint.route('/match')
def match():
    return render_template('match.html')


@monitor_blueprint.route('/teams')
def teams():
    return render_template('teams.html')


@controller_blueprint.route('/matchdata')
def matchdata():
    match = Match.query.filter_by(id=MATCH_ID).first()
    team_a = Team.query.filter_by(id=match.team_a).first()
    team_b = Team.query.filter_by(id=match.team_b).first()
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

                    'match': {'id': match.id,
                              'match_length': match.match_length,
                              'seconds': match.seconds

                             }
                    })

@controller_blueprint.route('/get-seconds')
def get_seconds():
    seconds = Match.query.filter_by(id=MATCH_ID).first().seconds
    return jsonify(seconds)

@timer_blueprint.route('/increment-seconds', methods=['GET', 'POST'])
def increment_seconds():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().seconds += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().seconds)


def get_tricot(team):
    if team.selected_tricot == 1:
        tricot = [team.home_color_one, team.home_color_two, team.home_color_three]
    else:
        tricot = [team.away_color_one, team.away_color_two, team.away_color_three]
    return tricot


if __name__ == '__main__':
    create_app().run(port=5555, use_reloader=False, debug=True)
