from flask import Flask, render_template, jsonify, current_app, Blueprint
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
    apscheduler.add_job(func=timer.start_timer, args=[app], id='timer')
    CORS(app)
    return app


# def scheduled_task(task_id):
#     for i in range(10):
#         time.sleep(1)
#         print('Task {} running iteration {}'.format(task_id, i))
#     <other stuff>
#     @app.before_first_request
#     def load_tasks():
#         from app import tasks






@monitor_blueprint.route('/')
def index():
    return 'Hello World'

@controller_blueprint.route('/start-timer/<is_act>')
def start_timer(is_act):
    Match.query.filter_by(id=MATCH_ID).first().is_timer_active = int(is_act)
    db.session.commit()
    return jsonify({'is_timer_active': Match.query.filter_by(id=MATCH_ID).first().is_timer_active})


@monitor_blueprint.route('/match')
def match():
    return render_template('match.html')


@monitor_blueprint.route('/teams')
def teams():
    return render_template('teams.html')


@monitor_blueprint.route('/matchdata')
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


if __name__ == '__main__':
    create_app().run(port=5555, use_reloader=False, debug=True)
