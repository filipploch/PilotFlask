from flask import Flask, render_template, jsonify, current_app, Blueprint, request, redirect, url_for
from flask_cors import CORS
from models import Team, Match, Player, MatchesData, Stadium
from database import db
from schemas import ma, player_schema, players_schema, match_datas_schema, team_schema, teams_schema, match_data_schema,\
    stadium_schema, matches_schema
import re
from timer import Timer
from variables import MATCH_ID, TEAM_A_ID, TEAM_B_ID
from flask_apscheduler import APScheduler
from collections import OrderedDict

monitor_blueprint = Blueprint('monitor', __name__)
controller_blueprint = Blueprint('controller', __name__)
timer_blueprint = Blueprint('timer', __name__)
settings_blueprint = Blueprint('settings', __name__)

apscheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hardsecretkey'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/futsal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(controller_blueprint)
    app.register_blueprint(timer_blueprint)
    app.register_blueprint(settings_blueprint)
    db.init_app(app)
    ma.init_app(app)
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

@monitor_blueprint.route('/start')
def start():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
                 }
    return render_template('start.html', logos=_logos, teams=_teams, match=_match_details)

@monitor_blueprint.route('/match-preview')
def match_preview():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
                 }
    return render_template('match-preview.html', logos=_logos, teams=_teams, match=_match_details)

def decode_date(date_to_decode):
    re_pattern = '^(\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2})$'
    return re.split(re_pattern, date_to_decode)


@monitor_blueprint.route('/match')
def match():
    return render_template('match.html')


@monitor_blueprint.route('/action')
def action():
    _action = MatchesData.query.filter_by(actual=1).first()
    if _action:
        _time = int(int(_action.time)/60 + 1)

        return render_template('action.html', action=match_data_schema.dump(_action), time_minutes=_time)
    return redirect(url_for('monitor.match'))


@monitor_blueprint.route('/teams')
def teams():
    _match = matchdata().get_json()
    _events = {'events_a': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                           , team_id=_match['teama']['id']
                                                           ).all(),
                 'events_b': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                           , team_id=_match['teamb']['id']
                                                           ).all()
                 }
    _strikers = {'strikers_a': get_strikers(_events['events_a']),
                 'strikers_b': get_strikers(_events['events_b'])}
    return render_template('teams.html', matchdata=_match, strikers=_strikers)


def get_strikers(events):
    strikers = OrderedDict()
    for event in events:
        striker_id = event.player_id
        goal_minute = int(int(event.time)/60 + 1)
        if striker_id not in strikers:
            strikers.update({striker_id: [goal_minute]})
        else:
            strikers[striker_id].append(goal_minute)
    return get_players_by_id(strikers)


def get_players_by_id(data: dict):
    new_data = []
    for key in data:
        data[key] = sorted(data[key])
        new_data.append([Player.query.filter_by(id=key).first(), ', '.join((str(x) + "'") for x in data[key])])
    return new_data


@monitor_blueprint.route('/lineup/<team>')
def lineup(team):
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _lineup = [player for player in _team.players if player.squad]
    _logo = _team.logo_file
    return render_template('lineup.html', _lineup=_lineup, _logo=_logo)


@controller_blueprint.route('/matchdata')
def matchdata():
    match = Match.query.filter_by(id=MATCH_ID).first()
    team_a = Team.query.filter_by(id=match.team_a).first()
    team_b = Team.query.filter_by(id=match.team_b).first()
    players_a = Player.query.filter_by(team=team_a.id).all()
    players_b = Player.query.filter_by(team=team_b.id).all()
    stadium = Stadium.query.filter_by(id=match.stadium).first()
    return jsonify({'teama': {'id': team_a.id,
                              'full_name': team_a.full_name,
                              'short_name': team_a.short_name,
                              'tricot': get_tricot(team_a),
                              'color_for_ui': team_a.color_for_ui,
                              'players': players_schema.dump(players_a),
                              'scores': match.score_a,
                              'fouls': match.fouls_a,
                              'logo_file': team_a.logo_file,
                              'selected_tricot': team_b.selected_tricot

                              },
                    'teamb': {'id': team_b.id,
                              'full_name': team_b.full_name,
                              'short_name': team_b.short_name,
                              'tricot': get_tricot(team_b),
                              'color_for_ui': team_b.color_for_ui,
                              'players': players_schema.dump(players_b),
                              'scores': match.score_b,
                              'fouls': match.fouls_b,
                              'logo_file': team_b.logo_file,
                              'selected_tricot': team_b.selected_tricot
                               },

                    'match': {'id': match.id,
                              'match_length': match.match_length,
                              'seconds': match.seconds,
                              'is_timer_countdown': match.is_timer_countdown,
                              'stadium': stadium_schema.dump(stadium),
                              'date': match.date
                             }
                    })


@controller_blueprint.route('/get-seconds')
def get_seconds():
    seconds = Match.query.filter_by(id=MATCH_ID).first().seconds
    return jsonify(seconds)


@controller_blueprint.route('/get-actual-match')
def get_actual_match():
    actual_match_id = Match.query.filter_by(actual=1).first().id
    return jsonify(actual_match_id)


@controller_blueprint.route('/set-timer-countdown', methods=['GET', 'POST'])
def set_timer_countdown():
    if request.method == 'POST':
        value = request.get_json()['is_timer_countdown']
        Match.query.filter_by(actual=1).first().is_timer_countdown = int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().seconds)


@controller_blueprint.route('/get-match-actions/<team_id>')
def get_match_actions(team_id):
    actual_match = matchdata().get_json()['match']
    actual_match_id = actual_match['id']
    match_actions = MatchesData.query.filter_by(match_id=actual_match_id, team_id=team_id).all()
    return match_datas_schema.dump(match_actions)


@controller_blueprint.route('/set-match-actions-non-actual', methods=['POST'])
def set_match_actions_non_actual():
    if request.method == 'POST':
        actual_match_id = matchdata().get_json()['match']['id']
        match_actions = MatchesData.query.filter_by(match_id=actual_match_id).all()
        for action in match_actions:
            action.actual = 0
            db.session.commit()
        return ''


@controller_blueprint.route('/update-match-actions', methods=['POST'])
def update_match_actions():
    if request.method == 'POST':
        response = request.get_json()
        print(response)
        match_data = MatchesData.query.filter_by(id=response['id']).first()
        match_data.time = response['time']
        match_data.player_id = response['player_id']
        match_data.action_id = response['action_id']
        db.session.add(match_data)
        db.session.commit()
        return 'match actions updated'


@controller_blueprint.route('/add-match-action', methods=['POST'])
def add_match_action():
    if request.method == 'POST':
        response = request.get_json()
        actual_match = Match.query.filter_by(actual=1).first()
        seconds = actual_match.seconds
        match_data = MatchesData(
            action_id=response['action_id'],
            player_id=response['player_id'],
            team_id=get_team_id_by_description(response['team'], actual_match),
            time=seconds,
            match_id=actual_match.id,
            actual=1
        )
        db.session.add(match_data)
        db.session.commit()
        return 'match action added'


def get_team_id_by_description(description, actual_match):
    if description == 'teama':
        return actual_match.team_a
    else:
        return actual_match.team_b


@controller_blueprint.route('/delete-match-action', methods=['POST'])
def delete_match_action():
    action_id = request.get_json()['action_id']
    action = MatchesData.query.filter_by(id=action_id).first()
    db.session.delete(action)
    db.session.commit()
    return ''


@controller_blueprint.route('/get-player/<player_id>')
def get_player(player_id):
    player = Player.query.filter_by(id=player_id).first()
    return player_schema.dump(player)


@timer_blueprint.route('/increment-seconds', methods=['GET', 'POST'])
def increment_seconds():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().seconds += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().seconds)


@controller_blueprint.route('/change-score-a', methods=['POST'])
def change_score_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().score_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().score_a)


@controller_blueprint.route('/change-score-b', methods=['POST'])
def change_score_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().score_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().score_b)


@controller_blueprint.route('/change-fouls-a', methods=['POST'])
def change_fouls_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().fouls_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().fouls_a)


@controller_blueprint.route('/change-fouls-b', methods=['POST'])
def change_fouls_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(id=MATCH_ID).first().fouls_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(id=MATCH_ID).first().fouls_b)


@controller_blueprint.route('/get-all-teams/<competition_id>')
def get_all_teams(competition_id):
    teams = Team.query.filter_by(competitions=competition_id).order_by(Team.full_name).all()
    return teams_schema.dump(teams)


@controller_blueprint.route('/get-team/<team_id>')
def get_team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    return team_schema.dump((team))


@controller_blueprint.route('/update-lineup', methods=['POST'])
def update_lineup():
    _player = request.get_json()
    player = Player.query.filter_by(id=_player['id']).first()
    player.squad = _player['squad']
    player.default_nr = _player['default_nr']
    player.first_name = _player['first_name']
    player.last_name = _player['last_name']
    player.position = set_position(_player['position'])
    player.captain = _player['captain']
    db.session.commit()
    return jsonify(Player.query.filter_by(id=_player['id']).first())


def set_position(position):
    if position:
        return 'Bramkarz'
    else:
        return ''


@controller_blueprint.route('/update-tricots', methods=['POST'])
def update_tricots():
    if request.method == 'POST':
        _team = request.get_json()
        team = Team.query.filter_by(id=_team['id']).first()
        team.home_color_one = _team['home_color_one']
        team.home_color_two = _team['home_color_two']
        team.home_color_three = _team['home_color_three']
        team.home_tricot_color_number = _team['home_tricot_color_number']
        team.away_color_one = _team['away_color_one']
        team.away_color_two = _team['away_color_two']
        team.away_color_three = _team['away_color_three']
        team.away_tricot_color_number = _team['away_tricot_color_number']
        team.bibs_color = _team['bibs_color']
        team.color_for_ui = _team['color_for_ui']
        team.selected_tricot = _team['selected_tricot']
        db.session.commit()
        return jsonify(Team.query.filter_by(id=_team['id']).first())


def get_tricot(team):
    if team.selected_tricot == 1:
        tricot = [team.home_color_one, team.home_color_two, team.home_color_three][:team.home_tricot_color_number]
    elif team.selected_tricot == 2:
        tricot = [team.away_color_one, team.away_color_two, team.away_color_three][:team.away_tricot_color_number]
    else:
        tricot = [team.bibs_color]
    return tricot

@settings_blueprint.route('/matches-settings', methods=['GET'])
def matches_settings():
    matches = Match.query.all()
    print(matches_schema.dump(matches), flush=True)
    return render_template('matches-settings.html', matches=matches_schema.dump(matches))



if __name__ == '__main__':
    create_app().run(port=5555, use_reloader=False, debug=True)
